from pathlib import Path
import csv,re,json,math
from collections import defaultdict
ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'
INTERIM=ROOT/'data'/'interim'
PROCESSED=ROOT/'data'/'processed'/'omal'
PROCESSED.mkdir(parents=True, exist_ok=True)
GROUPS=['g1_food','g2_housing','g3_household_articles','g4_clothing','g5_transport','g6_health_personal','g7_personal_expenses','g8_education','g9_communication']
GROUP_LABELS={'g1_food':'Alimentação e bebidas','g2_housing':'Habitação','g3_household_articles':'Artigos de residência','g4_clothing':'Vestuário','g5_transport':'Transportes','g6_health_personal':'Saúde e cuidados pessoais','g7_personal_expenses':'Despesas pessoais','g8_education':'Educação','g9_communication':'Comunicação'}

def readcsv(path):
    with open(path,encoding='utf-8-sig') as f:return list(csv.DictReader(f))
def num(x):
    try:return float(x)
    except:return float('nan')
def writecsv(path,rows,fields):
    with open(path,'w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rows)

est=readcsv(PROCESSED/'omal_fullgroups_pof_base.csv')
ipca=readcsv(INTERIM/'ipca_all_groups_city_monthly.csv')
cum={(r['city'],r['group_key'],r['date']):num(r['cum_index']) for r in ipca}
dates=sorted({r['date'] for r in ipca if r['group_key']=='g1_food'})
bridge=1.0375*1.0431;AE=2.1
monthly=[]
for e in est:
    city=e['city'];base=num(e['base_total_per_ae_2018'])*bridge
    for dt in dates:
        comps={g:base*num(e['share_'+g])*cum[(city,g,dt)]*AE for g in GROUPS}
        monthly.append({'city':city,'region':e['region'],'variant':e['variant'],'date':dt,'household_type':'2 adults + 2 children','adult_equivalents':AE,**comps,'omal_total':sum(comps.values()),'sample_n':num(e['sample_n']),'effective_n':num(e['effective_n']),'shrinkage_city_weight':num(e['shrinkage_city_weight'])})

# parse June 2026 minimum and DIEESE
months={'Janeiro':1,'Fevereiro':2,'Março':3,'Abril':4,'Maio':5,'Junho':6,'Julho':7,'Agosto':8,'Setembro':9,'Outubro':10,'Novembro':11,'Dezembro':12}
text=(RAW/'dieese'/'dieese_minimum_wage_monthly_1994_2026.txt').read_text(encoding='utf-8-sig');year=None;mw=dieese=None
pat=re.compile(r'^(Janeiro|Fevereiro|Março|Abril|Maio|Junho|Julho|Agosto|Setembro|Outubro|Novembro|Dezembro)\s+R\$\s*([\d.]+,\d{2})\s+R\$\s*([\d.]+,\d{2})$')
def br(s):return float(s.replace('.','').replace(',','.'))
for line in text.splitlines():
    line=line.strip()
    if re.fullmatch(r'\d{4}',line):year=int(line);continue
    m=pat.match(line)
    if m and year==2026 and months[m.group(1)]==6:mw=br(m.group(2));dieese=br(m.group(3))
latest_date=max(r['date'] for r in monthly)
hh_types={'1 adult':1.0,'1 adult + 1 child':1.3,'1 adult + 2 children':1.6,'2 adults':1.5,'2 adults + 1 child':1.8,'2 adults + 2 children':2.1}
latest=[]
for r in [x for x in monthly if x['date']==latest_date]:
    for name,ae in hh_types.items():
        scale=ae/AE; row={'city':r['city'],'region':r['region'],'variant':r['variant'],'date':r['date'],'household_type':name,'adult_equivalents':ae}
        for g in GROUPS:row[g]=r[g]*scale
        row['omal_total']=r['omal_total']*scale;row['one_worker_required_income']=row['omal_total'];row['two_worker_required_income_each']=row['omal_total']/2
        row['sample_n']=r['sample_n'];row['effective_n']=r['effective_n'];row['shrinkage_city_weight']=r['shrinkage_city_weight']
        row['statutory_minimum']=mw;row['multiple_of_minimum_one_worker']=row['omal_total']/mw;row['multiple_of_minimum_two_workers_each']=row['omal_total']/(2*mw)
        row['dieese_family_benchmark']=dieese;row['ratio_to_dieese_family']=row['omal_total']/dieese
        latest.append(row)
# PNAD latest
pnad_latest={}
for r in readcsv(INTERIM/'pnad_city_labour_income_quarterly.csv'):
    city=r['city'];q=r['quarter'];v=num(r['labour_income_real'])
    if city not in pnad_latest or q>pnad_latest[city][0]:pnad_latest[city]=(q,v)
for r in latest:
    qv=pnad_latest.get(r['city']);r['pnad_quarter']=qv[0] if qv else '';r['labour_income_real']=qv[1] if qv else float('nan')
summary=[r for r in latest if r['variant']=='core' and r['household_type']=='2 adults + 2 children']
summary.sort(key=lambda r:r['omal_total'],reverse=True)
# old comparison
old_latest={}
for r in readcsv(INTERIM/'omal_monthly_2020_2026_simplified.csv'):
    if r['date'].startswith('2026-06') and r['household_type']=='2 adults + 2 children':old_latest[(r['city'],r['variant'])]=num(r['omal_total'])
comparison=[]
for r in [x for x in latest if x['household_type']=='2 adults + 2 children']:
    old=old_latest.get((r['city'],r['variant']),float('nan'));new=r['omal_total']
    comparison.append({'city':r['city'],'region':r['region'],'variant':r['variant'],'old_omal_3_indices':old,'new_omal_9_groups':new,'absolute_change':new-old,'percent_change':new/old-1})
comparison.sort(key=lambda r:(r['variant'],r['city']))

monthly_fields=['city','region','variant','date','household_type','adult_equivalents']+GROUPS+['omal_total','sample_n','effective_n','shrinkage_city_weight']
hh_fields=['city','region','variant','date','household_type','adult_equivalents']+GROUPS+['omal_total','one_worker_required_income','two_worker_required_income_each','sample_n','effective_n','shrinkage_city_weight','statutory_minimum','multiple_of_minimum_one_worker','multiple_of_minimum_two_workers_each','dieese_family_benchmark','ratio_to_dieese_family','pnad_quarter','labour_income_real']
writecsv(PROCESSED/'omal_fullgroups_monthly_2020_2026.csv',monthly,monthly_fields)
writecsv(PROCESSED/'omal_fullgroups_latest_household_types.csv',latest,hh_fields)
writecsv(PROCESSED/'omal_fullgroups_summary_june2026.csv',summary,hh_fields)
writecsv(PROCESSED/'omal_fullgroups_comparison_old_new.csv',comparison,['city','region','variant','old_omal_3_indices','new_omal_9_groups','absolute_change','percent_change'])
# metadata merge
meta=json.loads((PROCESSED/'omal_fullgroups_pof_stage_metadata.json').read_text(encoding='utf-8'))
meta.update({'bridge_to_dec2019':bridge,'latest_date':latest_date,'statutory_minimum':mw,'dieese_family_benchmark':dieese,'group_labels':GROUP_LABELS})
(PROCESSED/'omal_fullgroups_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print('latest',latest_date,'rows',len(monthly),'summary')
for r in summary:print(r['city'],round(r['omal_total'],2),round(r['ratio_to_dieese_family'],3))
