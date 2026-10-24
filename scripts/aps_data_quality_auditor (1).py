"""Audit CDSS SOC 242 Cell 119 public county-month data.

Usage:
    python aps_data_quality_auditor.py --current SOC242FFY25-26.xlsx --out audit_results
    python aps_data_quality_auditor.py --current SOC242FFY25-26.xlsx \
        --previous master_soc242.csv --out audit_results

Historical differences compare a prior *processed extract* unless both inputs are
original official releases. Differences are not necessarily CDSS revisions.
"""
import argparse
import re
from pathlib import Path
import pandas as pd


def normalize(values):
    result = values.astype('string').str.strip()
    result = result.replace({'': pd.NA, 'nan': pd.NA, '<NA>': pd.NA})
    return result.fillna('<BLANK>')


def load_records(path):
    path = Path(path)
    if path.suffix.lower() in {'.xlsx', '.xlsm'}:
        data = pd.read_excel(path, sheet_name='Data_External', header=4)
    elif path.suffix.lower() == '.csv':
        data = pd.read_csv(path, low_memory=False)
    else:
        raise ValueError('Supply a CDSS .xlsx workbook or a SOC 242 .csv extract')
    required = {'County Name', 'Date', '119'}
    if not required.issubset(data.columns):
        raise ValueError(f'Missing columns: {sorted(required - set(data.columns))}')
    data = data[['County Name', 'Date', '119']].copy()
    data['County Name'] = data['County Name'].astype('string').str.strip()
    data['Date'] = pd.to_datetime(data['Date'], errors='coerce').dt.normalize()
    data = data[data['County Name'].notna() & (data['County Name'] != 'Statewide')].copy()
    if data['Date'].isna().any():
        raise ValueError('Some county records have unparseable dates')
    data['value'] = normalize(data['119'])
    return data[['County Name', 'Date', 'value']]


def load_notes(path):
    path = Path(path)
    if path.suffix.lower() not in {'.xlsx', '.xlsm'}:
        return None
    notes = pd.read_excel(path, sheet_name='Release Summary', header=3)
    if not {'REPORT MONTH', 'COMMENTS'}.issubset(notes.columns):
        raise ValueError('Could not read the workbook Release Summary')
    notes['REPORT MONTH'] = pd.to_datetime(notes['REPORT MONTH'], errors='coerce').dt.normalize()
    return notes


def build_documented(notes, county_names):
    documented = set()
    if notes is None:
        return documented
    for _, row in notes.iterrows():
        comment = str(row['COMMENTS'])
        date = row['REPORT MONTH']
        match = re.search(r'not reporting\s*:\s*(.*)', comment, flags=re.I | re.S)
        if pd.isna(date) or not match:
            continue
        text = match.group(1)
        for county in county_names:
            if re.search(r'(?<!\w)' + re.escape(str(county)) + r'(?!\w)', text, flags=re.I):
                documented.add((str(county), date))
    return documented


def run_audit(current_path, previous_path=None):
    data = load_records(current_path)
    notes = load_notes(current_path)
    numeric = pd.to_numeric(data['value'].replace('<BLANK>', pd.NA), errors='coerce')
    blank = data['value'].eq('<BLANK>')
    suppressed = data['value'].eq('*')
    invalid = (~blank & ~suppressed & (numeric.isna() | (numeric < 0) |
               (numeric % 1 != 0) | numeric.between(1, 10))).fillna(False)
    duplicates = data.duplicated(['County Name', 'Date'], keep=False)
    documented = build_documented(notes, data['County Name'].unique())
    blanks = data[blank].copy()
    blanks['documented_nonreporting'] = [
        (str(c), d) in documented for c, d in zip(blanks['County Name'], blanks['Date'])
    ]
    unexplained = blanks[~blanks['documented_nonreporting']].copy()
    # Check missing full rows, not just blank Cell 119 values.
    months = pd.date_range(data['Date'].min(), data['Date'].max(), freq='MS')
    expected = pd.MultiIndex.from_product(
        [sorted(data['County Name'].unique()), months], names=['County Name', 'Date'])
    actual = pd.MultiIndex.from_frame(data[['County Name', 'Date']])
    missing_rows = expected.difference(actual).to_frame(index=False)

    summary = pd.DataFrame([{
        'county_month_records': len(data), 'counties': data['County Name'].nunique(),
        'duplicate_rows': int(duplicates.sum()), 'missing_county_month_rows': len(missing_rows),
        'numeric': int(numeric.notna().sum()), 'suppressed': int(suppressed.sum()),
        'blanks': int(blank.sum()),
        'documented_nonreporting': int(blanks['documented_nonreporting'].sum()),
        'unexplained_blanks': len(unexplained), 'invalid_values': int(invalid.sum())
    }])
    differences = pd.DataFrame(columns=['County Name', 'Date', 'old_value', 'new_value'])
    if previous_path:
        previous = load_records(previous_path).rename(columns={'value': 'old_value'})
        current = data.rename(columns={'value': 'new_value'})
        if previous.duplicated(['County Name', 'Date']).any() or current.duplicated(['County Name', 'Date']).any():
            raise ValueError('Cannot compare versions containing duplicate county-month keys')
        overlap = previous.merge(current, on=['County Name', 'Date'], how='inner', validate='one_to_one')
        differences = overlap[overlap['old_value'] != overlap['new_value']].copy()
        differences = differences.sort_values(['Date', 'County Name'])
    return summary, unexplained, differences, missing_rows, data[invalid].copy()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--current', required=True, help='Current official CDSS SOC 242 workbook')
    parser.add_argument('--previous', help='Previous workbook or archived CSV, optional')
    parser.add_argument('--out', default='aps_audit_results', help='Output folder')
    args = parser.parse_args()
    results = run_audit(args.current, args.previous)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    names = ['audit_summary', 'unexplained_blanks', 'historical_differences',
             'missing_county_month_rows', 'invalid_values']
    for name, data in zip(names, results):
        data.to_csv(out / f'{name}.csv', index=False)
    print(results[0].to_string(index=False))
    print(f'Historical differences: {len(results[2])}')
    print(f'Saved five CSV files to {out}')

if __name__ == '__main__':
    main()
