import pandas as pd,numpy as np,json
from scipy.optimize import minimize
from scipy.special import logsumexp
from scipy.stats import nbinom
from sklearn.preprocessing import StandardScaler
from pathlib import Path
P=Path(__file__).resolve().parents[1]/'data'/'source';# Ordered model reconstruction; working notebook not required
soc=pd.read_csv(P/'master_soc242.csv',low_memory=False);master=pd.read_csv(P/'county_master_verified.csv');pop=pd.read_csv(P/'county_annual_65plus_population_2019_2024.csv');fy=['19-20','20-21','21-22','22-23','23-24','24-25']
d=soc.loc[soc.Fiscal_Year.isin(fy)&soc['County Name'].ne('Statewide')].copy();d['blank']=d[[str(i) for i in range(1,359)]].isna().all(axis=1);raw=d['119'].astype('string').str.strip();d['suppressed']=raw.eq('*').fillna(False);d['exact_count']=pd.to_numeric(raw,errors='coerce');d=d.loc[~d.blank].copy()
features=['poverty_rate_percent','broadband_percent','senior_disability_percent','living_alone_65_plus_percent','RUCC_2023'];d=d.merge(master[['county']+features],left_on='County Name',right_on='county',validate='many_to_one').merge(pop[['County Name','Fiscal_Year','population_65_plus']],on=['County Name','Fiscal_Year'],validate='many_to_one');d['calendar_month']=pd.to_datetime(d.Date).dt.month
print('rows',len(d),'exact',d.exact_count.notna().sum(),'supp',d.suppressed.sum(),'predictor missing',d[features].isna().sum().sum(),flush=True)
assert len(d)==4096 and d.exact_count.notna().sum()==2901 and d.suppressed.sum()==1195 and d[features+['population_65_plus']].notna().all().all()
Z=StandardScaler().fit_transform(d[features].astype(float)); names=[x+'_z' for x in features];d[names]=Z
Xdf=pd.concat([pd.Series(1.,index=d.index,name='Intercept'),d[names],pd.get_dummies(d.Fiscal_Year,prefix='FY',drop_first=True,dtype=float),pd.get_dummies(d.calendar_month,prefix='month',drop_first=True,dtype=float)],axis=1);X=Xdf.to_numpy(float);off=np.log(d.population_65_plus.to_numpy(float));y=d.exact_count.to_numpy(float);exact=(~d.suppressed).to_numpy(bool);supp=(d.suppressed).to_numpy(bool)
print('X shape',X.shape,'columns',Xdf.columns.tolist(),flush=True)
def nll(par):
 alpha=np.exp(par[-1]);mu=np.exp(np.clip(X@par[:-1]+off,-30,30));size=1/alpha;prob=size/(size+mu)
 ll=nbinom.logpmf(y[exact].astype(int),size,prob[exact]).sum()
 ll+=logsumexp(np.vstack([nbinom.logpmf(k,size,prob[supp]) for k in range(1,11)]),axis=0).sum()
 return -ll if np.isfinite(ll) else 1e100
start=np.zeros(X.shape[1]+1);start[0]=np.log(np.nansum(y)/d.population_65_plus.sum());start[-1]=np.log(.1)
rows=[];best=None
for a in [.03,.05,.1,.2,.4]:
 st=start.copy();st[-1]=np.log(a);r=minimize(nll,st,method='L-BFGS-B',bounds=[(None,None)]*X.shape[1]+[(np.log(1e-4),np.log(10))],options={'maxiter':10000,'ftol':1e-12,'gtol':1e-7,'maxls':50});rows.append({'start_alpha':a,'success':r.success,'NLL':r.fun,'alpha':np.exp(r.x[-1]),'iterations':r.nit});print(rows[-1],flush=True)
 if best is None or r.fun<best.fun:best=r
pd.DataFrame(rows).to_csv(P.parents[1]/'results'/'verified'/'association_multistart_recomputed.csv',index=False)
pd.DataFrame({'variable':Xdf.columns,'coefficient':best.x[:-1],'IRR':np.exp(best.x[:-1])}).to_csv(P.parents[1]/'results'/'verified'/'association_point_estimates_recomputed.csv',index=False)
print('BEST',best.fun,np.exp(best.x[-1]),'success',best.success,flush=True)
