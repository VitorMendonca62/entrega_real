"""Deduplica o dataset unificado e gera todos os splits dos experimentos (determinístico, seed 42).
Uso: python -I preparar_splits.py <dataset_anotado.csv> <pasta_saida> [<BrScamsFacebook.xlsx original>]
Saídas: pool_dedup.csv, dedup_removidos.csv, splits.json, resumo_splits.json
Regras: duplicatas removidas ANTES de separar; sintéticos só em treino/validação; teste = só Facebook ("Interno")
(ou, no leave-one-source-out, uma fonte real inteira); validação sempre tirada do treino, nunca do teste.
"""
import sys, json, re, unicodedata, hashlib
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import StratifiedKFold, train_test_split

SRC, OUT = sys.argv[1], sys.argv[2]
SEED=42; COS=0.85; K=5; VAL_FRAC=0.10
LABELS=["Relacionamento","Financeiro","Phishing","Loja Falsa","Desinformação","Seguro"]   # == id2label do plugin (0..5)
L2I={c:i for i,c in enumerate(LABELS)}
def norm(t):
    t=unicodedata.normalize("NFKC",str(t)).lower().strip().strip('"')
    return re.sub(r"\s+"," ",re.sub(r"https?://\S+","<url>",t))

d=pd.read_csv(SRC); d["norm"]=d.Mensagem.map(norm); d["label"]=d.classe.map(L2I)
orig_norm=set()
if len(sys.argv)>3:
    o=pd.read_excel(sys.argv[3]); orig_norm=set(o.Mensagem.map(norm))
d["in_original"]=d.norm.isin(orig_norm) if orig_norm else ~d.fonte.isin(["Dados Sintéticos","Telegram/Wpp Dataset"])

# --- duplicatas: exatas + quase (cosseno de n-gramas de caractere >= COS), em componentes conexos
X=TfidfVectorizer(analyzer="char_wb",ngram_range=(4,5),sublinear_tf=True).fit_transform(d.norm)
S=cosine_similarity(X); np.fill_diagonal(S,0)
par=list(range(len(d)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
exact=d.groupby("norm").indices
for ix in exact.values():
    for a in ix[1:]: par[f(a)]=f(ix[0])
ii,jj=np.where(np.triu(S>=COS))
for a,b in zip(ii,jj): par[f(a)]=f(b)
d["cluster"]=[f(i) for i in range(len(d))]
prio=lambda r:(0 if r.tipo=="real" else 1, 0 if r.facebook else 1, r.linha_xlsx)
manter=[]; rem=[]
for c,g in d.groupby("cluster"):
    if len(g)==1: manter.append(g.index[0]); continue
    if g.classe.nunique()>1:                       # mesmo texto com rótulos diferentes: ambíguo, descarta todos
        rem+= [(i,"cluster com rótulos conflitantes") for i in g.index]; continue
    keep=sorted(g.index,key=lambda i:prio(g.loc[i]))[0]; manter.append(keep)
    rem+=[(i,f"duplicata/quase-duplicata de linha {int(d.linha_xlsx[keep])}") for i in g.index if i!=keep]
pool=d.loc[sorted(manter)].reset_index(drop=True)
rm=d.loc[[i for i,_ in rem],["linha_xlsx","fonte","classe","Mensagem"]].copy(); rm["motivo"]=[m for _,m in rem]
cols=["linha_xlsx","Mensagem","classe","label","fonte","tipo","facebook","in_original","plataforma","idioma"]
pool[cols].to_csv(f"{OUT}/pool_dedup.csv",index=False); rm.to_csv(f"{OUT}/dedup_removidos.csv",index=False)
ID=lambda x:[int(v) for v in x]

def tira_val(treino):
    """validação estratificada tirada do treino, só de dados reais (representa o uso real)"""
    real=treino[treino.tipo=="real"]
    _,v=train_test_split(real,test_size=VAL_FRAC,stratify=real.label,random_state=SEED)
    return treino.drop(v.index), v
def exp(treino,teste):
    tr,v=tira_val(treino)
    return {"train":ID(tr.linha_xlsx),"val":ID(v.linha_xlsx),"test":ID(teste.linha_xlsx) if teste is not None else []}
braco={"A":pool[pool.in_original],"B":pool,"C":pool[pool.tipo=="real"]}
fb=pool[pool.facebook].reset_index(drop=True)
sp={}
# 1) Facebook-CV: cada mensagem do Facebook é testada uma vez, sem nunca estar no treino do seu fold
skf=StratifiedKFold(n_splits=K,shuffle=True,random_state=SEED)
folds=[fb.iloc[te] for _,te in skf.split(fb,fb.label)]
for b,p in braco.items():
    for k,te in enumerate(folds,1):
        tr=p[~p.linha_xlsx.isin(te.linha_xlsx)]; sp[f"fbcv_{b}_f{k}"]=exp(tr,te)
# 2) leave-one-source-out (fonte real inteira fora do treino e do val); sintéticos ficam no treino
fontes=["Interno"]+[f"Externo {i}" for i in range(1,8)]+["Telegram/Wpp Dataset"]
for s in fontes:
    te=pool[pool.fonte==s]
    sp[f"loso_B_{s.replace(' ','').replace('/','-')}"]=exp(pool[pool.fonte!=s],te)
    if s!="Telegram/Wpp Dataset":               # braço A (dados originais) só tem as fontes originais
        sp[f"loso_A_{s.replace(' ','')}"]=exp(braco["A"][braco["A"].fonte!=s],te)
# 3) modelo candidato (todos os dados; avaliado pelo Facebook-CV acima)
sp["final_B"]=exp(pool,None)
json.dump({"seed":SEED,"labels":LABELS,"k_fb":K,"cos_dedup":COS,"splits":sp},open(f"{OUT}/splits.json","w"))

# verificações das regras
bad=[]
for n,s in sp.items():
    t,v,e=set(s["train"]),set(s["val"]),set(s["test"])
    if t&e or v&e or t&v: bad.append((n,"interseção"))
    sint=set(pool[pool.tipo=="sintético"].linha_xlsx)
    if e&sint: bad.append((n,"sintético no teste"))
    if n.startswith("fbcv") and not e<=set(fb.linha_xlsx): bad.append((n,"teste não-Facebook"))
    if n.startswith("loso_") and n.startswith("loso_B") and (set(pool[pool.fonte.isin([x for x in fontes if n.endswith(x.replace(' ','').replace('/','-'))])].linha_xlsx)&(t|v)): bad.append((n,"fonte vazou"))
assert not bad,bad
res={"linhas_originais":len(d),"removidas":len(rm),"pool":len(pool),"removidas_por_motivo":rm.motivo.str.split(" de linha").str[0].value_counts().to_dict(),
 "pool_por_classe":pool.classe.value_counts().to_dict(),"facebook_por_classe":fb.classe.value_counts().to_dict(),
 "braco_A":len(braco["A"]),"braco_B":len(braco["B"]),"braco_C":len(braco["C"]),
 "sha256_pool":hashlib.sha256(open(f"{OUT}/pool_dedup.csv","rb").read()).hexdigest(),
 "tamanhos":{n:{k:len(v) for k,v in s.items()} for n,s in sp.items()},
 "fb_folds_por_classe":[fo.classe.value_counts().sort_index().to_dict() for fo in folds]}
json.dump(res,open(f"{OUT}/resumo_splits.json","w"),ensure_ascii=False,indent=1)
print(json.dumps({k:res[k] for k in res if k!="tamanhos"},ensure_ascii=False,indent=1)); print(len(sp),"experimentos")
