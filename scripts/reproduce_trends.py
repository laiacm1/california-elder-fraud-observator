import pandas as pd,numpy as np
from scipy.optimize import minimize
from scipy.stats import nbinom,chi2
from scipy.special import logsumexp
from statsmodels.stats.multitest import multipletests
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'data'/'source';soc=pd.read_csv(P/'master_soc242.csv',low_memory=False);pop=pd.read_csv(P/'county_annual_65plus_population_2019_2024.csv')
years=['19-20','20-21','21-22','22-23','23-24','24-25'];d=soc[soc.Fiscal_Year.isin(years)&soc['County Name'].ne('Statewide')].copy();d['blank']=d[[str(i) for i in range(1,359)]].isna().all(axis=1);raw=d['119'].astype('string').str.strip();d['suppressed']=raw.eq('*').fillna(False);d['count']=pd.to_numeric(raw,errors='coerce');d=d[~d.blank].copy().merge(pop[['County Name','Fiscal_Year','population_65_plus']],on=['County Name','Fiscal_Year'],validate='many_to_one');d['Date']=pd.to_datetime(d.Date);start=d.Date.min();d['month_index']=(d.Date.dt.year-start.year)*12+d.Date.dt.month-start.month

def fit_model(t,include_time,klo,khi):
 y=t['count'].to_numpy(float);cens=t.suppressed.to_numpy(bool);exact=~cens;off=np.log(t.population_65_plus.to_numpy(float));X=np.column_stack([np.ones(len(t)),t.month_index.to_numpy(float)]) if include_time else np.ones((len(t),1))
 def nll(p):
  mu=np.exp(np.clip(X@p[:-1]+off,-30,30));size=np.exp(-p[-1]);prob=size/(size+mu); ll=nbinom.logpmf(y[exact].astype(int),size,prob[exact]).sum()
  if cens.any():ll+=logsumexp(np.vstack([nbinom.logpmf(k,size,prob[cens]) for k in range(klo,khi+1)]),axis=0).sum()
  return -ll if np.isfinite(ll) else 1e100
 v=t.loc[~t.suppressed,'count'].sum();e=t.loc[~t.suppressed,'population_65_plus'].sum();params=np.zeros(X.shape[1]+1);params[0]=np.log(max(v/e,1e-8));params[-1]=np.log(.15)
 return minimize(nll,params,method='L-BFGS-B',bounds=[(None,None)]*X.shape[1]+[(np.log(1e-4),np.log(10))])
all_rows=[]
for a,b in [(1,10),(0,11)]:
 rows=[]
 for idx,(county,t) in enumerate(d.groupby('County Name')):
  null=fit_model(t,False,a,b);trend=fit_model(t,True,a,b);lr=max(2*(null.fun-trend.fun),0);rows.append(dict(county=county,p=chi2.sf(lr,1),beta_month=trend.x[1],annual_percent_change=(np.exp(12*trend.x[1])-1)*100,trend_converged=trend.success,null_converged=null.success,alpha=np.exp(trend.x[-1])))
  if idx%20==0:print(a,b,idx,county,flush=True)
 frame=pd.DataFrame(rows);frame['q']=multipletests(frame.p,method='fdr_bh')[1];frame['classification']=np.where(frame.q>=.05,'No clear trend',np.where(frame.beta_month>0,'Increasing','Decreasing'));frame['interval']=f'{a}-{b}';all_rows.append(frame);print('RESULT',a,b,frame.classification.value_counts().to_dict(),'converged',frame.trend_converged.sum(),frame.null_converged.sum(),flush=True)
result=pd.concat(all_rows);result.to_csv(P.parents[1]/'results'/'verified'/'county_trend_suppression_interval_sensitivity_recomputed.csv',index=False);wide=result.pivot(index='county',columns='interval',values='classification');print('CHANGED',wide[wide['1-10']!=wide['0-11']].to_string());print('BOUND ALPHA',result.groupby('interval').apply(lambda x:((x.alpha<.00011)|(x.alpha>9.99)).sum()).to_dict())
