from pathlib import Path
import json,pandas as pd
HERE=Path(__file__).resolve().parent; OUT=HERE.parent/'treasury_output'; DEST=HERE/'data'/'dashboard_data.js'
def read(n):
 p=OUT/n
 if not p.exists(): raise FileNotFoundError(f'Missing required file: {p}')
 return pd.read_csv(p)
credit=read('credit_market_history.csv');buckets=read('treasury_maturity_buckets.csv');summary=read('treasury_security_summary.csv');refi=read('treasury_refinancing_summary.csv');dur=read('treasury_duration_by_class.csv')
wall=pd.read_csv(OUT/'treasury_maturity_wall.csv') if (OUT/'treasury_maturity_wall.csv').exists() else pd.DataFrame();sec=pd.read_csv(OUT/'treasury_latest_mspd_clean.csv') if (OUT/'treasury_latest_mspd_clean.csv').exists() else pd.DataFrame()
credit['date']=pd.to_datetime(credit['date'],errors='coerce');credit=credit.dropna(subset=['date']).sort_values('date');latest=credit.dropna(subset=['ust_10y_pct','bbb_oas_bp']).iloc[-1]
total=float(pd.to_numeric(sec['outstanding_amt'],errors='coerce').sum()/1e6) if not sec.empty else float(summary['outstanding_trillions'].sum());wam=float((summary.outstanding_trillions*summary.weighted_avg_maturity_years).sum()/summary.outstanding_trillions.sum());nom=dur[dur.security_class.isin(['Bills','Notes','Bonds'])];moddur=float((nom.outstanding_trillions*nom.modified_duration).sum()/nom.outstanding_trillions.sum())
# latest MSPD date from file contents where possible
mspd=''
for c in sec.columns if not sec.empty else []:
 if 'record_date' in c.lower() or 'snapshot' in c.lower():
  vals=pd.to_datetime(sec[c],errors='coerce').dropna()
  if not vals.empty: mspd=vals.max().date().isoformat();break
history=[]
for _,r in credit.iterrows():
 f=lambda n: None if pd.isna(r.get(n)) else float(r[n])
 history.append({'date':r.date.date().isoformat(),'ust10':f('ust_10y_pct'),'real10':f('ust_10y_real_pct'),'ig':f('ig_oas_bp'),'bbb':f('bbb_oas_bp'),'hy':f('hy_oas_bp'),'ust10_5d_bp':f('ust_10y_chg_5d_bp'),'bbb_5d_bp':f('bbb_oas_chg_5d_bp')})
if not wall.empty:
 first=wall.columns[0]
 if first!='maturity_year': wall=wall.rename(columns={first:'maturity_year'})
data={'meta':{'market_date':latest.date.date().isoformat(),'mspd_date':mspd,'curve_date':'','generated':pd.Timestamp.now().date().isoformat()},'market':{'ust10':float(latest.ust_10y_pct),'real10':float(latest.ust_10y_real_pct),'ig_oas':float(latest.ig_oas_bp),'bbb_oas':float(latest.bbb_oas_bp),'hy_oas':float(latest.hy_oas_bp),'ust10_1d_bp':float(latest.ust_10y_chg_1d_bp),'bbb_1d_bp':float(latest.bbb_oas_chg_1d_bp),'ust10_5d_bp':float(latest.ust_10y_chg_5d_bp),'bbb_5d_bp':float(latest.bbb_oas_chg_5d_bp),'regime':str(latest.regime_5d).capitalize(),'alert_1d':bool(latest.double_tightening_1d),'alert_5d':bool(latest.double_tightening_5d)},'debt':{'marketable_debt_trillions':total,'wam_years':wam,'modified_duration_years':moddur,'maturity_buckets':[{'horizon':f'{int(r.horizon_years)} year'+('s' if int(r.horizon_years)!=1 else ''),'amount':float(r.amount_trillions),'share':float(r.share_pct)} for _,r in buckets.iterrows()],'composition':[{'security':str(r.security_class),'amount':float(r.outstanding_trillions),'share':float(r.share_pct),'wam':float(r.weighted_avg_maturity_years)} for _,r in summary.iterrows()]},'refinancing':[{'year':int(r.maturity_year),'maturing':float(r.debt_maturing_trillions),'coupon':float(r.avg_existing_coupon_pct),'replacement':float(r.avg_replacement_yield_pct),'reset_bp':float(r.avg_rate_change_bp),'interest_change':float(r.annual_interest_change_billions)} for _,r in refi.iterrows()],'credit_history':history,'maturity_wall':wall.to_dict(orient='records') if not wall.empty else []}
DEST.parent.mkdir(parents=True,exist_ok=True);DEST.write_text('window.DASHBOARD_DATA = '+json.dumps(data,allow_nan=False)+';\n',encoding='utf-8');print(f'Wrote {DEST}');print(f'Latest market date: {data["meta"]["market_date"]}')
