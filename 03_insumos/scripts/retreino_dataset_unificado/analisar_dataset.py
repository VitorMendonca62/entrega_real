"""Análise do BrScamsFacebook_Unificado_2.xlsx (sem treinar nada).
Uso: python -I analisar_dataset.py <xlsx> <pasta_saida>
"""
import sys, json, re, hashlib, unicodedata
import numpy as np, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

XLSX, OUT = sys.argv[1], sys.argv[2]
SEED = 42
CURTO = {"Golpes Baseados Em Relacionamento":"Relacionamento","Golpes de Ganho Financeiro Ilusório":"Financeiro",
         "Ataques de Phishing e Roubo de Dados":"Phishing","Fraudes em Lojas Virtuais Falsas":"Loja Falsa",
         "Golpes de Desinformação Digital":"Desinformação","Seguro":"Seguro"}
# Origem/idioma conforme a Tabela 1 do artigo (fontes em inglês passaram por tradução automática)
ORIGEM = {
 "Interno":("Facebook (personas)","nativo PT"),
 "Externo 1":("ScamWarners – Romance","traduzido EN→PT"),
 "Externo 2":("Kaggle – SMS Spam Collection","traduzido EN→PT"),
 "Externo 3":("Kaggle – Fake News Portuguese","nativo PT"),
 "Externo 4":("GitHub sec-fraudimabr (WhatsApp/Telegram)","nativo PT"),
 "Externo 5":("ScamWarners – Financial","traduzido EN→PT"),
 "Externo 6":("Kaggle – Fake Reviews","traduzido EN→PT"),
 "Externo 7":("ScamWarners – Online Selling","traduzido EN→PT"),
 "Telegram/Wpp Dataset":("Telegram/WhatsApp (novo)","nativo PT"),
 "Dados Sintéticos":("Sintético (gerado)","nativo PT (gerado)"),
}
def norm(t):
    t=unicodedata.normalize("NFKC",str(t)).lower().strip().strip('"')
    t=re.sub(r"https?://\S+","<url>",t); t=re.sub(r"\s+"," ",t)
    return t

d=pd.read_excel(XLSX,sheet_name="Página1"); d["linha_xlsx"]=d.index+2
d["classe"]=d.Categoria.map(CURTO); assert d.classe.notna().all()
d["fonte"]=d.Dataset; d["norm"]=d.Mensagem.map(norm)
d["tipo"]=np.where(d.fonte=="Dados Sintéticos","sintético","real")
d["idioma"]=d.fonte.map(lambda f:ORIGEM[f][1]); d["plataforma"]=d.fonte.map(lambda f:ORIGEM[f][0])
d["facebook"]=d.fonte.eq("Interno")
d["n_chars"]=d.Mensagem.str.len()
res={}
res["n_linhas"]=len(d)
res["classes"]=d.classe.value_counts().to_dict()
res["fontes"]=d.fonte.value_counts().to_dict()
res["fonte_pct"]=(d.fonte.value_counts(normalize=True)*100).round(1).to_dict()
res["tipo"]=d.tipo.value_counts().to_dict()
res["idioma"]=d.idioma.value_counts().to_dict()
res["facebook_por_classe"]=d[d.facebook].classe.value_counts().to_dict()
ct=pd.crosstab(d.fonte,d.classe); ct.to_csv(f"{OUT}/matriz_fonte_x_classe.csv")
# pureza: fração da classe explicada pela fonte dominante / fonte -> classe
res["fonte_classe_dominante_pct"]={f:round(float(ct.loc[f].max()/ct.loc[f].sum()*100),1) for f in ct.index}
# informação mútua normalizada fonte-classe (quão previsível é a classe só pela fonte)
from sklearn.metrics import normalized_mutual_info_score as nmi
res["NMI_fonte_classe"]=round(float(nmi(d.fonte,d.classe)),3)
# acurácia de um "classificador só-fonte" (classe majoritária por fonte)
maj=ct.idxmax(axis=1); res["acuracia_so_pela_fonte_pct"]=round(float((d.fonte.map(maj)==d.classe).mean()*100),1)
# Seguro por fonte
res["seguro_por_fonte"]=d[d.classe=="Seguro"].fonte.value_counts().to_dict()
# duplicatas exatas
d["h"]=d.norm.map(lambda s:hashlib.md5(s.encode()).hexdigest())
g=d.groupby("h")
ex=d[d.duplicated("h",keep=False)].sort_values("h")
res["dup_exatas_linhas"]=int(d.duplicated("h",keep="first").sum())
res["dup_exatas_grupos"]=int(ex.h.nunique())
res["dup_exatas_conflito_classe"]=int((g.classe.nunique()>1).sum())
# quase-duplicatas: tf-idf de n-gramas de caractere, cosseno
vec=TfidfVectorizer(analyzer="char_wb",ngram_range=(4,5),min_df=1,sublinear_tf=True)
X=vec.fit_transform(d.norm); S=cosine_similarity(X,dense_output=True); np.fill_diagonal(S,0)
for th in (0.95,0.9,0.85,0.8,0.7):
    ii,jj=np.where(np.triu(S>=th)); res[f"pares_quase_dup_cos>={th}"]=int(len(ii))
TH=0.85
ii,jj=np.where(np.triu(S>=TH))
# componentes conexos
par=list(range(len(d)))
def f(a):
    while par[a]!=a: par[a]=par[par[a]]; a=par[a]
    return a
for a,b in zip(ii,jj): par[f(a)]=f(b)
d["cluster"]=[f(i) for i in range(len(d))]
cs=d.groupby("cluster").size(); res["clusters_quase_dup(th=0.85)"]=int((cs>1).sum())
res["linhas_removiveis_th0.85"]=int(len(d)-d.cluster.nunique())
cf=d.groupby("cluster").agg(n=("classe","size"),nclasse=("classe","nunique"),nfonte=("fonte","nunique"))
res["clusters_com_classes_conflitantes"]=int(((cf.n>1)&(cf.nclasse>1)).sum())
res["clusters_misturando_real_e_sintetico"]=int((d.groupby("cluster").tipo.nunique()>1).sum())
# onde estão as quase-duplicatas
rem=d[d.duplicated("cluster",keep="first")]
res["removiveis_por_fonte_th0.85"]=rem.fonte.value_counts().to_dict()
res["removiveis_por_classe_th0.85"]=rem.classe.value_counts().to_dict()
# sintético vs real: sintético parecido com real?
sint=np.where(d.tipo=="sintético")[0]; real=np.where(d.tipo=="real")[0]
mx=S[np.ix_(sint,real)].max(axis=1); res["sintetico_cos_max_com_real"]={"mediana":round(float(np.median(mx)),3),"p90":round(float(np.percentile(mx,90)),3),">=0.7":int((mx>=0.7).sum())}
# sintético vs sintético
mxs=S[np.ix_(sint,sint)].max(axis=1); res["sintetico_cos_max_entre_si"]={"mediana":round(float(np.median(mxs)),3),">=0.85":int((mxs>=0.85).sum())}
# interno (facebook) vs resto
fb=np.where(d.facebook)[0]; ot=np.where(~d.facebook)[0]
res["facebook_com_vizinho_cos>=0.7_em_outra_fonte"]=int((S[np.ix_(fb,ot)].max(axis=1)>=0.7).sum())
# traduzidos: resquícios de inglês / estrutura
EN={"the","and","you","your","for","with","that","this","have","from","are","was","will","not"}
def en_ratio(t):
    w=re.findall(r"[a-zà-ú']+",t.lower()); 
    return sum(x in EN for x in w)/max(len(w),1)
d["en_ratio"]=d.norm.map(en_ratio)
res["resquicio_ingles_(>=10% palavras EN)_por_fonte"]=d[d.en_ratio>=.10].fonte.value_counts().to_dict()
# tamanho por fonte e por classe (viés de comprimento)
res["chars_mediana_por_fonte"]=d.groupby("fonte").n_chars.median().round(0).to_dict()
res["chars_mediana_por_classe"]=d.groupby("classe").n_chars.median().round(0).to_dict()
# 'Seguro' vs scam por comprimento dentro da mesma fonte
res["chars_seguro_vs_golpe_por_fonte"]={f:{"seguro":float(x[x.classe=='Seguro'].n_chars.median()) if (x.classe=='Seguro').any() else None,
   "golpe":float(x[x.classe!='Seguro'].n_chars.median()) if (x.classe!='Seguro').any() else None} for f,x in d.groupby("fonte")}
# emojis/hashtags/urls por fonte
d["emoji"]=d.Mensagem.map(lambda t:sum(ord(c)>0x1F000 for c in str(t))>0)
d["hashtag"]=d.Mensagem.str.contains(r"#\w+"); d["url"]=d.Mensagem.str.contains(r"https?://|www\.")
res["pct_emoji_hashtag_url_por_fonte"]=d.groupby("fonte")[["emoji","hashtag","url"]].mean().mul(100).round(0).to_dict("index")
# aba Candidatos
c=pd.read_excel(XLSX,sheet_name="Candidatos"); c["norm"]=c.Mensagem.map(norm)
pn=set(d.norm); res["candidatos_total"]=len(c); res["candidatos_ja_na_Pagina1"]=int(c.norm.isin(pn).sum())
res["candidatos_classes"]=c.Categoria.value_counts().to_dict()
json.dump(res,open(f"{OUT}/analise_dataset.json","w"),ensure_ascii=False,indent=1,default=str)
d.drop(columns=["norm"]).to_csv(f"{OUT}/dataset_anotado.csv",index=False)
# exemplos de quase-duplicatas
ex=[]
for a,b in list(zip(ii,jj))[:4000:max(1,len(ii)//12)]:
    ex.append({"cos":round(float(S[a,b]),3),"fonte_a":d.fonte[a],"fonte_b":d.fonte[b],"classe_a":d.classe[a],"classe_b":d.classe[b],"a":d.Mensagem[a][:110],"b":d.Mensagem[b][:110]})
json.dump(ex,open(f"{OUT}/exemplos_quase_duplicatas.json","w"),ensure_ascii=False,indent=1)
print(json.dumps(res,ensure_ascii=False,indent=1,default=str))
