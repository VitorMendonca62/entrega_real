"""Compara os braços (A = dados originais, B = unificado, C = unificado sem sintéticos) a partir dos resultados do treino.
Uso: python -I comparar.py <resultados_retreino> <dados_retreino> <saida.md> [<saida.json>]
Todos os números saem de predicoes.csv por exemplo (sem recalcular modelo). Seed fixa nos bootstraps."""
import sys, os, json, glob, numpy as np, pandas as pd
from math import comb
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix
R,D,OUT=sys.argv[1:4]; OJ=sys.argv[4] if len(sys.argv)>4 else None
LAB=["Relacionamento","Financeiro","Phishing","Loja Falsa","Desinformação","Seguro"]; SEG=5
pool=pd.read_csv(f"{D}/pool_dedup.csv").set_index("linha_xlsx")
rng=np.random.default_rng(42)
def le(exp):
    f=f"{R}/{exp}/predicoes.csv"; return pd.read_csv(f) if os.path.exists(f) else None
def fbcv(b):
    fr=[le(f"fbcv_{b}_f{k}") for k in range(1,6)]
    return None if any(x is None for x in fr) else pd.concat(fr,ignore_index=True)
def f1m(y,p,labs=range(6)): return f1_score(y,p,labels=list(labs),average="macro",zero_division=0)
def f1c(y,p,c): return f1_score(y,p,labels=[c],average=None,zero_division=0)[0]
def boot(y,p,fn,B=2000):
    n=len(y); v=[]; 
    for _ in range(B):
        i=rng.integers(0,n,n); v.append(fn(y[i],p[i]))
    return np.percentile(v,[2.5,97.5])
def mcnemar(ok1,ok2):
    b=int((ok1&~ok2).sum()); c=int((~ok1&ok2).sum()); n=b+c
    if n==0: return b,c,1.0
    k=min(b,c); p=min(1.0,2*sum(comb(n,i) for i in range(k+1))/2**n); return b,c,p
def tab_met(df):
    y,p=df.y.values,df.pred.values; r={"n":len(y),"acc":accuracy_score(y,p),"f1_macro":f1m(y,p)}
    r["f1_macro_ic95"]=boot(y,p,f1m).tolist(); r["seguro_f1_ic95"]=boot(y,p,lambda a,b:f1c(a,b,SEG)).tolist()
    r["f1"]={LAB[c]:f1c(y,p,c) for c in range(6)}
    seg=y==SEG; r["seguro_recall"]=float((p[seg]==SEG).mean()); r["seguro_precisao"]=float((y[p==SEG]==SEG).mean()) if (p==SEG).any() else 0.0
    r["alarme_falso_(Seguro→golpe)"]=float((p[seg]!=SEG).mean()); r["golpe_perdido_(golpe→Seguro)"]=float((p[~seg]==SEG).mean())
    r["matriz"]=confusion_matrix(y,p,labels=list(range(6))).tolist(); return r
L=[]; J={}
P=lambda s="":L.append(s)
P("# Resultados do retreino — comparação entre modelos\n")
P("_Gerado por `scripts/comparar.py` a partir de `predicoes.csv` por exemplo. Todas as métricas do Facebook são **fora da amostra**: cada mensagem do Facebook só é testada por modelos que não a viram._\n")
arms={b:fbcv(b) for b in "ABC"}
P("## 1. Facebook-CV (60 mensagens do Facebook, cada uma testada uma vez)\n")
base={}
for b,nm in [("A","A — dados originais (445)"),("B","B — unificado (751)"),("C","C — unificado sem sintéticos (541)")]:
    if arms[b] is not None: base[b]=tab_met(arms[b]); J[f"fbcv_{b}"]=base[b]
if base:
    P("| Braço | n | Acurácia | F1 macro [IC95%] | F1 Seguro [IC95%] | Recall Seguro | Precisão Seguro | Alarme falso (Seguro→golpe) | Golpe perdido (golpe→Seguro) |"); P("|---|---:|---:|---|---|---:|---:|---:|---:|")
    for b,m in base.items():
        P(f"| {b} | {m['n']} | {m['acc']:.3f} | {m['f1_macro']:.3f} [{m['f1_macro_ic95'][0]:.2f}–{m['f1_macro_ic95'][1]:.2f}] | {m['f1']['Seguro']:.3f} [{m['seguro_f1_ic95'][0]:.2f}–{m['seguro_f1_ic95'][1]:.2f}] | {m['seguro_recall']:.2f} | {m['seguro_precisao']:.2f} | {m['alarme_falso_(Seguro→golpe)']:.2f} | {m['golpe_perdido_(golpe→Seguro)']:.2f} |")
    P("\nF1 por classe:\n"); P("| Braço | "+" | ".join(LAB)+" |"); P("|---|"+"---:|"*6)
    for b,m in base.items(): P(f"| {b} | "+" | ".join(f"{m['f1'][c]:.2f}" for c in LAB)+" |")
    P("\nMatriz de confusão (linhas = verdadeiro, colunas = previsto; ordem: "+", ".join(LAB)+"):\n")
    for b,m in base.items():
        P(f"**Braço {b}**\n\n```"); 
        for c,row in zip(LAB,m["matriz"]): P(f"{c:15s} "+" ".join(f"{v:3d}" for v in row))
        P("```\n")
    P("### Comparações pareadas (mesmas 60 mensagens)\n"); P("| Comparação | Δ acurácia | Δ F1 macro [IC95% bootstrap] | McNemar b/c | p exato |"); P("|---|---:|---|---:|---:|")
    for x,y in [("B","A"),("C","A"),("B","C")]:
        if x in arms and y in arms and arms[x] is not None and arms[y] is not None:
            m=arms[x].merge(arms[y],on="linha_xlsx",suffixes=("_x","_y")); yv=m.y_x.values; px,py=m.pred_x.values,m.pred_y.values
            b,c,p=mcnemar(px==yv,py==yv); n=len(yv); d=[]
            for _ in range(2000):
                i=rng.integers(0,n,n); d.append(f1m(yv[i],px[i])-f1m(yv[i],py[i]))
            lo,hi=np.percentile(d,[2.5,97.5]); P(f"| {x} − {y} | {(px==yv).mean()-(py==yv).mean():+.3f} | {f1m(yv,px)-f1m(yv,py):+.3f} [{lo:+.2f}, {hi:+.2f}] | {b}/{c} | {p:.3f} |")
            J[f"pareado_{x}_{y}"]={"d_acc":float((px==yv).mean()-(py==yv).mean()),"d_f1":float(f1m(yv,px)-f1m(yv,py)),"ic95":[float(lo),float(hi)],"mcnemar":[b,c,p]}
    P("\n_McNemar: b = acertou só o 1º modelo, c = acertou só o 2º. Com n=60 e 4–17 por classe, os intervalos são largos._\n")
# baseline = modelos já treinados
P("## 2. Modelo atual × modelo novo (mesmas 60 mensagens do Facebook)\n")
P("O modelo atual e as duas replicações (treinados só com os 450 originais) viram ~90% destas mensagens no treino: os números deles estão **inflados por vazamento**. "
  "Mesmo assim é a referência do que o plugin faz hoje.\n")
P("| Modelo | Fora da amostra? | Acurácia | F1 macro | F1 Seguro | Alarme falso (Seguro→golpe) | Golpe perdido (golpe→Seguro) |"); P("|---|---|---:|---:|---:|---:|---:|")
for n,f in (("**Atual — no plugin** (checkpoint publicado brunanoroes/veritaplugin-bert)","pred_plugin_publicado.csv"),
            ("Replicação 1 (Colab 20/10)","pred_1a_execucao.csv"),("Replicação 2 (Colab 26/10)","pred_2a_execucao.csv")):
    pf=os.path.join(D,"..","baseline",f)
    if os.path.exists(pf):
        q=pd.read_csv(pf); q=q[q.facebook&q.linha_xlsx.isin(pool.index)]; q=q.assign(y=q.classe.map(LAB.index),pred=q.pred.map(LAB.index))
        m=tab_met(q); J[f"atual_{f[5:7]}"]=m
        P(f"| {n} | não (~90% vazado) | {m['acc']:.3f} | {m['f1_macro']:.3f} | {m['f1']['Seguro']:.3f} | {m['alarme_falso_(Seguro→golpe)']:.2f} | {m['golpe_perdido_(golpe→Seguro)']:.2f} |")
for b,nm in (("A","Retreino só com dados originais (A)"),("B","**Novo — dataset unificado (B)**"),("C","Unificado sem sintéticos (C)")):
    if b in base: m=base[b]; P(f"| {nm} | sim | {m['acc']:.3f} | {m['f1_macro']:.3f} | {m['f1']['Seguro']:.3f} | {m['alarme_falso_(Seguro→golpe)']:.2f} | {m['golpe_perdido_(golpe→Seguro)']:.2f} |")
P("\n_A comparação justa é A × B: mesmo código, mesmos folds, ambos fora da amostra. Se B supera o modelo atual mesmo com o atual favorecido pelo vazamento, o ganho real é ainda maior._\n")
# LOSO
P("## 3. Leave-one-source-out (a fonte inteira fica fora do treino e da validação)\n")
rows=[]
for s in ["Interno"]+[f"Externo{i}" for i in range(1,8)]+["Telegram-WppDataset"]:
    r={"fonte":s}
    for b in "AB":
        f=f"{R}/loso_{b}_{s}/resultado.json"
        if os.path.exists(f):
            j=json.load(open(f)); r[b]=(j["acc"],j["f1_macro_classes_presentes"],j["n_teste"])
    if len(r)>1: rows.append(r)
if rows:
    P("| Fonte (fora) | n | Acurácia A | Acurácia B | F1 macro* A | F1 macro* B | Δ acurácia (B−A) |"); P("|---|---:|---:|---:|---:|---:|---:|")
    for r in rows:
        a,b=r.get("A"),r.get("B"); n=(a or b)[2]; fm=lambda t,i:f"{t[i]:.2f}" if t else "—"
        d=f"{b[0]-a[0]:+.2f}" if a and b else "—"; P(f"| {r['fonte']} | {n} | {fm(a,0)} | {fm(b,0)} | {fm(a,1)} | {fm(b,1)} | {d} |")
    P("\n*F1 macro só sobre as classes presentes na fonte (várias fontes têm 1 ou 2 classes: nelas a acurácia é o recall da classe). Telegram/Wpp não existe no braço A. "
      "Queda forte com a fonte fora = o modelo dependia do estilo da fonte.\n")
    J["loso"]=rows
# reais x sintéticos
P("## 4. Dados reais × sintéticos\n")
if base.get("B") and base.get("C"):
    P(f"- **Efeito de pôr os sintéticos no treino** (teste real = Facebook-CV): B (com) F1 macro {base['B']['f1_macro']:.3f}, F1 Seguro {base['B']['f1']['Seguro']:.3f}; "
      f"C (sem) F1 macro {base['C']['f1_macro']:.3f}, F1 Seguro {base['C']['f1']['Seguro']:.3f}. Teste pareado B − C na seção 1.")
rows_s=[]
for b in "AC":
    fr=[f"{R}/fbcv_{b}_f{k}/predicoes_sinteticos_diag.csv" for k in range(1,6)]
    fr=[pd.read_csv(f) for f in fr if os.path.exists(f)]
    if fr:
        accs=[(x.y==x.pred).mean() for x in fr]; allp=pd.concat(fr)
        rows_s.append((b,len(fr),np.mean(accs),f1m(allp.y.values,allp.pred.values),f1c(allp.y.values,allp.pred.values,SEG)))
if rows_s:
    P("\n**Diagnóstico (não é teste):** modelos que nunca viram sintéticos classificando os 210 sintéticos. Acerto alto = sintético parecido com o real; baixo = distribuição diferente.\n")
    P("| Braço | folds | Acurácia média | F1 macro | F1 Seguro |"); P("|---|---:|---:|---:|---:|")
    for b,k,ac,fm_,fs in rows_s: P(f"| {b} | {k} | {ac:.3f} | {fm_:.3f} | {fs:.3f} |")
    J["sinteticos_diag"]=[dict(zip(("braco","folds","acc","f1_macro","f1_seguro"),r)) for r in rows_s]
P("\n_Regra do protocolo: sintéticos nunca entram no teste; por isso não existe \"acurácia em sintéticos\" do modelo B._\n")
# erros
P("## 5. Principais erros do braço B no Facebook-CV\n")
if arms["B"] is not None:
    e=arms["B"].copy(); e=e[e.y!=e.pred]; e["verd"]=e.y.map(dict(enumerate(LAB))); e["prev"]=e.pred.map(dict(enumerate(LAB)))
    P("Confusões mais frequentes (verdadeiro → previsto):\n"); 
    for (v,p),n in e.groupby(["verd","prev"]).size().sort_values(ascending=False).head(8).items(): P(f"- {v} → {p}: {n}")
    P("\nErros de maior confiança (o modelo errou com convicção):\n"); P("| linha xlsx | verdadeiro → previsto | conf. | texto |"); P("|---:|---|---:|---|")
    for _,r in e.sort_values("conf",ascending=False).head(12).iterrows():
        t=str(pool.loc[r.linha_xlsx,"Mensagem"]).replace("\n"," ").replace("|","/")[:110]; P(f"| {r.linha_xlsx} | {r.verd} → {r.prev} | {r.conf:.2f} | {t} |")
    P()
    s=arms["B"]; s=s[(s.y==SEG)&(s.pred!=SEG)]
    if len(s): 
        P("Mensagens seguras do Facebook classificadas como golpe:\n")
        for _,r in s.iterrows(): P(f"- linha {r.linha_xlsx} → {LAB[int(r.pred)]} (conf. {r.conf:.2f}): {str(pool.loc[r.linha_xlsx,'Mensagem']).replace(chr(10),' ')[:110]}")
# critério de decisão (fixado antes dos resultados)
P("\n## 6. Critério de decisão (definido antes de ver os resultados)\n")
P("O modelo B só é recomendado para exportação se **todos** valerem:\n\n1. F1 macro de B ≥ F1 macro de A + 0,03 no Facebook-CV;\n2. F1 do Seguro de B ≥ F1 do Seguro de A, sem aumentar o alarme falso (Seguro→golpe) em mais de 0,05;\n3. Acurácia de B no leave-Interno-out ≥ a de A;\n4. Nenhuma fonte com queda de acurácia > 0,15 em B frente a A no leave-one-source-out;\n5. F1 macro e F1 do Seguro de B ≥ os do modelo atual do plugin nas mesmas 60 mensagens (mesmo com o vazamento a favor do atual).\n")
if "fbcv_A" in J and "fbcv_B" in J:
    a,b=J["fbcv_A"],J["fbcv_B"]; lo=next((r for r in rows if r["fonte"]=="Interno"),None)
    c1=b["f1_macro"]>=a["f1_macro"]+0.03; c2=b["f1"]["Seguro"]>=a["f1"]["Seguro"] and b["alarme_falso_(Seguro→golpe)"]<=a["alarme_falso_(Seguro→golpe)"]+0.05
    c3=(lo["B"][0]>=lo["A"][0]) if lo and "A" in lo and "B" in lo else None
    c4=all(r["B"][0]-r["A"][0]>=-0.15 for r in rows if "A" in r and "B" in r)
    pl=J.get("atual_pl"); c5=(b["f1_macro"]>=pl["f1_macro"] and b["f1"]["Seguro"]>=pl["f1"]["Seguro"]) if pl else None
    P("| Critério | Atendido |\n|---|---|"); 
    for i,c in enumerate((c1,c2,c3,c4,c5),1): P(f"| {i} | {'sim' if c else ('não' if c is not None else 'não avaliável (faltam resultados)')} |")
    J["criterios"]=[c1,c2,c3,c4,c5]
else: P("_Faltam resultados dos braços A e B para aplicar o critério._")
open(OUT,"w").write("\n".join(L)); 
if OJ: json.dump(J,open(OJ,"w"),ensure_ascii=False,indent=1,default=float)
print("ok",OUT)
