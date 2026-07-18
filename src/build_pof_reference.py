from zipfile import ZipFile
from collections import defaultdict
from pathlib import Path
from lxml import etree
import numpy as np
import xlrd
import csv, re, json, math, time, unicodedata

ROOT=Path(__file__).resolve().parents[1]
RAW=ROOT/'data'/'raw'
PROCESSED=ROOT/'data'/'processed'/'omal'
PROCESSED.mkdir(parents=True, exist_ok=True)
DATA_ZIP=RAW/'ibge_pof'/'Dados_20230713.zip'

CITY_SPECS={
    'Rio Branco': ('12', set(range(1201,1202))),
    'São Luís': ('21', set(range(2101,2104))),
    'Aracaju': ('28', set(range(2801,2803))),
    'Campo Grande': ('50', set(range(5001,5004))),
    'Goiânia': ('52', set(range(5201,5204))),
    'Brasília': ('53', set(range(5301,5307))),
    'Belém': ('15', set(range(1501,1504))),
    'Fortaleza': ('23', set(range(2301,2307))),
    'Recife': ('26', set(range(2601,2604))),
    'Salvador': ('29', set(range(2901,2907))),
    'Belo Horizonte': ('31', set(range(3101,3107))),
    'Grande Vitória': ('32', set(range(3201,3206))),
    'Rio de Janeiro': ('33', set(range(3301,3310))),
    'São Paulo': ('35', set(range(3501,3510))),
    'Curitiba': ('41', set(range(4101,4106))),
    'Porto Alegre': ('43', set(range(4301,4307))),
}
UF_STRATUM_TO_CITY={(uf,s):city for city,(uf,ss) in CITY_SPECS.items() for s in ss}
CITY_REGION={
    'Rio Branco':'North','Belém':'North',
    'São Luís':'Northeast','Aracaju':'Northeast','Fortaleza':'Northeast','Recife':'Northeast','Salvador':'Northeast',
    'Belo Horizonte':'Southeast','Grande Vitória':'Southeast','Rio de Janeiro':'Southeast','São Paulo':'Southeast',
    'Curitiba':'South','Porto Alegre':'South',
    'Campo Grande':'Center-West','Goiânia':'Center-West','Brasília':'Center-West',
}
TARGET_TERRITORIES={
    'Rio Branco (AC)':'Rio Branco','São Luís (MA)':'São Luís','Aracaju (SE)':'Aracaju',
    'Campo Grande (MS)':'Campo Grande','Goiânia (GO)':'Goiânia','Brasília (DF)':'Brasília',
    'Belém (PA)':'Belém','Fortaleza (CE)':'Fortaleza','Recife (PE)':'Recife','Salvador (BA)':'Salvador',
    'Belo Horizonte (MG)':'Belo Horizonte','Grande Vitória (ES)':'Grande Vitória',
    'Rio de Janeiro (RJ)':'Rio de Janeiro','São Paulo (SP)':'São Paulo',
    'Curitiba (PR)':'Curitiba','Porto Alegre (RS)':'Porto Alegre',
}
IPCA_CATEGORIES={
    'Índice geral':'general',
    '1.Alimentação e bebidas':'g1_food',
    '2.Habitação':'g2_housing',
    '3.Artigos de residência':'g3_household_articles',
    '4.Vestuário':'g4_clothing',
    '5.Transportes':'g5_transport',
    '6.Saúde e cuidados pessoais':'g6_health_personal',
    '7.Despesas pessoais':'g7_personal_expenses',
    '8.Educação':'g8_education',
    '9.Comunicação':'g9_communication',
}
GROUP_LABELS={
    'g1_food':'Alimentação e bebidas',
    'g2_housing':'Habitação',
    'g3_household_articles':'Artigos de residência',
    'g4_clothing':'Vestuário',
    'g5_transport':'Transportes',
    'g6_health_personal':'Saúde e cuidados pessoais',
    'g7_personal_expenses':'Despesas pessoais',
    'g8_education':'Educação',
    'g9_communication':'Comunicação',
}
GROUPS=list(GROUP_LABELS)

# ---------------- Fixed-width helpers ----------------
def city_from_prefix(line):
    try:return UF_STRATUM_TO_CITY.get((line[0:2], int(line[2:6])))
    except:return None

def sfloat(s, default=np.nan):
    s=s.strip()
    if not s:return default
    try:return float(s)
    except:return default

def sint(s, default=None):
    s=s.strip()
    if not s:return default
    try:return int(s)
    except:return default

def offsets(widths,names):
    pos=0; out={}
    for w,n in zip(widths,names):out[n]=(pos,pos+w);pos+=w
    return out

def val(line, off, name):
    a,b=off[name]; return line[a:b]

def key_uc(line, off):
    return (val(line,off,'UF').strip(),val(line,off,'ESTRATO_POF').strip(),val(line,off,'COD_UPA').strip(),val(line,off,'NUM_DOM').strip(),val(line,off,'NUM_UC').strip())

def key_dom(line, off):
    return (val(line,off,'UF').strip(),val(line,off,'ESTRATO_POF').strip(),val(line,off,'COD_UPA').strip(),val(line,off,'NUM_DOM').strip())

MORADOR_WIDTHS=[2,4,1,9,2,1,2,2,1,2,2,4,3,1,1,1,1,1,2,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,2,1,1,2,1,1,2,1,1,1,2,1,2,14,14,10,1,20,20,20,20]
MORADOR_NAMES=['UF','ESTRATO_POF','TIPO_SITUACAO_REG','COD_UPA','NUM_DOM','NUM_UC','COD_INFORMANTE','V0306','V0401','V04021','V04022','V04023','V0403','V0404','V0405','V0406','V0407','V0408','V0409','V0410','V0411','V0412','V0413','V0414','V0415','V0416','V041711','V041712','V041721','V041722','V041731','V041732','V041741','V041742','V0418','V0419','V0420','V0421','V0422','V0423','V0424','V0425','V0426','V0427','V0428','V0429','V0430','ANOS_ESTUDO','PESO','PESO_FINAL','RENDA_TOTAL','NIVEL_INSTRUCAO','RENDA_DISP_PC','RENDA_MONET_PC','RENDA_NAO_MONET_PC','DEDUCAO_PC']
MORADOR_OFF=offsets(MORADOR_WIDTHS,MORADOR_NAMES)
DOM_WIDTHS=[2,4,1,9,2,1,1,1,1,2,1,1,1,1,1,1,1,1,1,2,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,14,14,1]
DOM_NAMES=['UF','ESTRATO_POF','TIPO_SITUACAO_REG','COD_UPA','NUM_DOM','V0201','V0202','V0203','V0204','V0205','V0206','V0207','V0208','V0209','V02101','V02102','V02103','V02104','V02105','V02111','V02112','V02113','V0212','V0213','V02141','V02142','V0215','V02161','V02162','V02163','V02164','V0217','V0219','V0220','V0221','PESO','PESO_FINAL','V6199']
DOM_OFF=offsets(DOM_WIDTHS,DOM_NAMES)
COND_WIDTHS=[2,4,1,9,2,1,2,1,6,5,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,14,14,10]
COND_NAMES=['UF','ESTRATO_POF','TIPO_SITUACAO_REG','COD_UPA','NUM_DOM','NUM_UC','COD_INFORMANTE','V6101','V6102','V6103','V61041','V61042','V61043','V61044','V61045','V61046','V61051','V61052','V61053','V61054','V61055','V61056','V61057','V61058','V61061','V61062','V61063','V61064','V61065','V61066','V61067','V61068','V61069','V610610','V610611','V61071','V61072','V61073','V6108','V6109','V6110','V6111','V6112','V6113','V6114','V6115','V6116','V6117','V6118','V6119','V6120','V6121','PESO','PESO_FINAL','RENDA_TOTAL']
COND_OFF=offsets(COND_WIDTHS,COND_NAMES)
EXP_SCHEMAS={
'ALUGUEL_ESTIMADO':([2,4,1,9,2,1,2,7,2,10,2,2,12,10,1,2,14,14,10],['UF','ESTRATO_POF','TIPO_SITUACAO_REG','COD_UPA','NUM_DOM','NUM_UC','QUADRO','V9001','V9002','V8000','V9010','V9011','DEFLATOR','V8000_DEFLA','COD_IMPUT_VALOR','FATOR_ANUALIZACAO','PESO','PESO_FINAL','RENDA_TOTAL']),
'DESPESA_COLETIVA':([2,4,1,9,2,1,2,2,7,2,4,10,2,2,1,10,1,12,10,10,1,1,2,14,14,10,5],['UF','ESTRATO_POF','TIPO_SITUACAO_REG','COD_UPA','NUM_DOM','NUM_UC','QUADRO','SEQ','V9001','V9002','V9005','V8000','V9010','V9011','V9012','V1904','V1905','DEFLATOR','V8000_DEFLA','V1904_DEFLA','COD_IMPUT_VALOR','COD_IMPUT_QUANTIDADE','FATOR_ANUALIZACAO','PESO','PESO_FINAL','RENDA_TOTAL','V9004']),
'CADERNETA_COLETIVA':([2,4,1,9,2,1,2,3,7,2,10,12,10,1,2,14,14,10,9,4,5,9,5],['UF','ESTRATO_POF','TIPO_SITUACAO_REG','COD_UPA','NUM_DOM','NUM_UC','QUADRO','SEQ','V9001','V9002','V8000','DEFLATOR','V8000_DEFLA','COD_IMPUT_VALOR','FATOR_ANUALIZACAO','PESO','PESO_FINAL','RENDA_TOTAL','V9005','V9007','V9009','QTD_FINAL','V9004']),
'DESPESA_INDIVIDUAL':([2,4,1,9,2,1,2,2,2,7,2,10,2,2,1,1,1,12,10,1,2,14,14,10,5],['UF','ESTRATO_POF','TIPO_SITUACAO_REG','COD_UPA','NUM_DOM','NUM_UC','COD_INFORMANTE','QUADRO','SEQ','V9001','V9002','V8000','V9010','V9011','V9012','V4104','V4105','DEFLATOR','V8000_DEFLA','COD_IMPUT_VALOR','FATOR_ANUALIZACAO','PESO','PESO_FINAL','RENDA_TOTAL','V9004'])}
EXP_OFF={k:offsets(*v) for k,v in EXP_SCHEMAS.items()}

# ---------------- Translator and mapping ----------------
sh=xlrd.open_workbook(str(RAW/'ibge_pof'/'translators'/'Tradutor_Despesa_Geral.xls')).sheet_by_index(0)
headers=sh.row_values(0); hi={h:i for i,h in enumerate(headers)}
translator={}
for r in range(1,sh.nrows):
    try: code=int(float(sh.cell_value(r,hi['Codigo'])))
    except: continue
    translator[code]={
        'd2':str(sh.cell_value(r,hi['Descricao_2'])).strip(),
        'd3':str(sh.cell_value(r,hi['Descricao_3'])).strip(),
        'd4':str(sh.cell_value(r,hi['Descricao_4'])).strip(),
        'd5':str(sh.cell_value(r,hi['Descricao_5'])).strip(),
    }

def map_ipca_group(d3,d4,d5):
    if d3=='Alimentacao': return 'g1_food'
    if d3=='Habitacao':
        if d4 in {'Mobiliario e artigos do  lar','Eletrodomesticos','Consertos de artigos do lar'}:
            return 'g3_household_articles'
        if d4 in {'Servicos e taxas','Servidos e taxas'} and d5 in {'Pacote de telefone, tv e internet','Telefone celular','Telefone fixo'}:
            return 'g9_communication'
        return 'g2_housing'
    if d3=='Vestuario': return 'g4_clothing'
    if d3=='Transporte': return 'g5_transport'
    if d3 in {'Assistencia a saude','Higiene e cuidados pessoais'}: return 'g6_health_personal'
    if d3 in {'Recreação e cultura','Serviços pessoais','Despesas diversas'}: return 'g7_personal_expenses'
    if d3=='Educacao': return 'g8_education'
    return None

def classify(meta):
    if meta is None or meta['d2']!='Despesas de Consumo': return None
    d3,d4,d5=meta['d3'],meta['d4'],meta['d5']
    group=map_ipca_group(d3,d4,d5)
    if group is None:return None
    core=True; expanded=True
    if group=='g3_household_articles': core=False
    if d3=='Transporte' and d4 in {'Aquisicao de veiculos','Viagens esporadicas'}:
        core=False
        if d4=='Aquisicao de veiculos': expanded=False
    if group=='g7_personal_expenses': core=False
    return {'group':group,'core':core,'expanded':expanded,'d3':d3,'d4':d4,'d5':d5}

# ---------------- POF extraction ----------------
print('POF: households',flush=True)
hh={}
with ZipFile(DATA_ZIP) as z, z.open('MORADOR.txt') as f:
    for raw in f:
        line=raw.decode('latin1').rstrip('\r\n')
        city=city_from_prefix(line)
        if not city:continue
        k=key_uc(line,MORADOR_OFF)
        relation=sint(val(line,MORADOR_OFF,'V0306'))
        if relation in (18,19):continue
        age=sint(val(line,MORADOR_OFF,'V0403'))
        if age is None:continue
        rec=hh.get(k)
        if rec is None:
            rec=hh[k]={'city':city,'n':0,'adults':0,'children':0,'weight':sfloat(val(line,MORADOR_OFF,'PESO_FINAL')),'income_pc':sfloat(val(line,MORADOR_OFF,'RENDA_DISP_PC'))}
        rec['n']+=1
        if age<14:rec['children']+=1
        else:rec['adults']+=1
for rec in hh.values():
    a=rec['adults']; c=rec['children']
    rec['ae']=(1.0+0.5*max(a-1,0)+0.3*c) if a+c>0 else np.nan
    rec['eq_income']=rec['income_pc']*rec['n']/rec['ae'] if rec['ae'] and np.isfinite(rec['income_pc']) else np.nan
print('target UCs',len(hh),flush=True)

food_secure={}
with ZipFile(DATA_ZIP) as z,z.open('DOMICILIO.txt') as f:
    for raw in f:
        line=raw.decode('latin1').rstrip('\r\n')
        if city_from_prefix(line):food_secure[key_dom(line,DOM_OFF)]=(sint(val(line,DOM_OFF,'V6199'))==1)
conditions={}
with ZipFile(DATA_ZIP) as z,z.open('CONDICOES_VIDA.txt') as f:
    for raw in f:
        line=raw.decode('latin1').rstrip('\r\n')
        if not city_from_prefix(line):continue
        k=key_uc(line,COND_OFF)
        arrears=(sint(val(line,COND_OFF,'V61071'))==1) or (sint(val(line,COND_OFF,'V61072'))==1)
        hunger=any(sint(val(line,COND_OFF,v))==1 for v in ['V6114','V6115','V6116','V6117','V6118','V6119','V6120','V6121'])
        conditions[k]={'arrears':arrears,'hunger':hunger}

expense=defaultdict(lambda:defaultdict(float)); map_counts=defaultdict(int)
with ZipFile(DATA_ZIP) as z:
    for source in ['ALUGUEL_ESTIMADO','DESPESA_COLETIVA','CADERNETA_COLETIVA','DESPESA_INDIVIDUAL']:
        t=time.time(); kept=0; off=EXP_OFF[source]
        with z.open(source+'.txt') as f:
            for raw in f:
                line=raw.decode('latin1').rstrip('\r\n')
                if not city_from_prefix(line):continue
                k=key_uc(line,off)
                if k not in hh:continue
                code7=sint(val(line,off,'V9001'))
                if code7 is None:continue
                meta=translator.get(code7//100); cls=classify(meta)
                if cls is None:continue
                v=sfloat(val(line,off,'V8000_DEFLA')); factor=sfloat(val(line,off,'FATOR_ANUALIZACAO'),1.0)
                if not np.isfinite(v) or not np.isfinite(factor):continue
                q=sint(val(line,off,'QUADRO'),0) or 0
                if source=='ALUGUEL_ESTIMADO':
                    months=sfloat(val(line,off,'V9011'),12.0); monthly=v*months*factor/12.0
                elif source=='DESPESA_COLETIVA':
                    months=sfloat(val(line,off,'V9011'),1.0); monthly=v*months*factor/12.0 if q in (10,19) else v*factor/12.0
                elif source=='CADERNETA_COLETIVA': monthly=v*factor/12.0
                else:
                    months=sfloat(val(line,off,'V9011'),1.0); monthly=v*months*factor/12.0 if q in (44,47,48,49,50) else v*factor/12.0
                if not np.isfinite(monthly) or monthly<0 or monthly>1e7:continue
                g=cls['group']
                expense[k]['all::'+g]+=monthly
                if cls['core']:expense[k]['core::'+g]+=monthly;expense[k]['core_total']+=monthly
                if cls['expanded']:expense[k]['expanded::'+g]+=monthly;expense[k]['expanded_total']+=monthly
                map_counts[g]+=1;kept+=1
        print(source,'kept',kept,'sec',round(time.time()-t,1),flush=True)

# list rows as dicts
households=[]
for k,rec in hh.items():
    domk=k[:4]; cond=conditions.get(k,{})
    if not (rec['ae']>0 and np.isfinite(rec['weight']) and np.isfinite(rec['eq_income'])):continue
    e=expense.get(k,{})
    if e.get('core_total',0)<=0:continue
    row=dict(rec)
    row['adequate_ref']=food_secure.get(domk,False) and not cond.get('arrears',False) and not cond.get('hunger',False)
    for variant in ['core','expanded']:
        row[variant+'_total']=e.get(variant+'_total',0.0)
        for g in GROUPS:row[variant+'::'+g]=e.get(variant+'::'+g,0.0)
    households.append(row)
print('usable UCs',len(households),flush=True)

# weighted stats
def wquantile(rows, value_fn, q):
    pairs=[(value_fn(r),r['weight']) for r in rows]
    pairs=[(v,w) for v,w in pairs if np.isfinite(v) and np.isfinite(w) and w>0]
    if not pairs:return np.nan
    pairs.sort(key=lambda x:x[0]); total=sum(w for _,w in pairs); cutoff=q*total; c=0
    for v,w in pairs:
        c+=w
        if c>=cutoff:return float(v)
    return float(pairs[-1][0])

def wmean(rows, value_fn):
    pairs=[(value_fn(r),r['weight']) for r in rows]
    pairs=[(v,w) for v,w in pairs if np.isfinite(v) and np.isfinite(w) and w>0]
    if not pairs:return np.nan
    sw=sum(w for _,w in pairs);return float(sum(v*w for v,w in pairs)/sw)

def neff(rows):
    ws=[r['weight'] for r in rows if np.isfinite(r['weight']) and r['weight']>0]
    return float(sum(ws)**2/sum(w*w for w in ws)) if ws else 0.0

adequate=[r for r in households if r['adequate_ref']]
p30=wquantile(adequate,lambda r:r['eq_income'],.30);p60=wquantile(adequate,lambda r:r['eq_income'],.60)
ref=[r for r in adequate if p30<=r['eq_income']<=p60]
print('reference',len(ref),'band',p30,p60,flush=True)

estimates=[]
for city in CITY_SPECS:
    cg=[r for r in ref if r['city']==city]
    rg=[r for r in ref if CITY_REGION[r['city']]==CITY_REGION[city]]
    for variant in ['core','expanded']:
        def pae(r):return r[variant+'_total']/r['ae']
        if cg:
            arr=sorted(pae(r) for r in cg);lo=np.quantile(arr,.02);hi=np.quantile(arr,.98);cgt=[r for r in cg if lo<=pae(r)<=hi]
        else:cgt=[]
        if rg:
            arr=sorted(pae(r) for r in rg);lo=np.quantile(arr,.02);hi=np.quantile(arr,.98);rgt=[r for r in rg if lo<=pae(r)<=hi]
        else:rgt=[]
        city_med=wquantile(cgt,pae,.5);reg_med=wquantile(rgt,pae,.5)
        n_eff=neff(cgt);lam=n_eff/(n_eff+80.0)
        total_pae=(lam*city_med+(1-lam)*reg_med) if np.isfinite(city_med) else reg_med
        shr={}
        for g in GROUPS:
            cm=wmean(cgt,lambda r,g=g:r[variant+'::'+g]/r['ae'])
            rm=wmean(rgt,lambda r,g=g:r[variant+'::'+g]/r['ae'])
            if not np.isfinite(cm):cm=0.0
            if not np.isfinite(rm):rm=0.0
            shr[g]=lam*cm+(1-lam)*rm
        ssum=sum(shr.values())
        shares={g:(shr[g]/ssum if ssum>0 else 0.0) for g in GROUPS}
        estimates.append({'city':city,'region':CITY_REGION[city],'variant':variant,'sample_n':len(cgt),'effective_n':n_eff,'shrinkage_city_weight':lam,'income_band_low':p30,'income_band_high':p60,'base_total_per_ae_2018':total_pae,**{'share_'+g:shares[g] for g in GROUPS}})


# write stage 1 estimates
fields=['city','region','variant','sample_n','effective_n','shrinkage_city_weight','income_band_low','income_band_high','base_total_per_ae_2018']+[f'share_{g}' for g in GROUPS]
with open(PROCESSED/'omal_fullgroups_pof_base.csv','w',encoding='utf-8-sig',newline='') as f:
    w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(estimates)
meta={'reference_income_p30':p30,'reference_income_p60':p60,'n_households':len(households),'n_reference':len(ref),'group_labels':GROUP_LABELS,'mapping_counts':dict(map_counts)}
(PROCESSED/'omal_fullgroups_pof_stage_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print('stage1 written',len(estimates))
