"""Linha de base: métricas dos modelos já treinados (execução 1 e 2) sobre o dataset unificado, com marcação de vazamento.
Uso: python -I resumo_baseline.py <pool_dedup.csv> <splits_originais_dir (holdout/*.csv)> <pred_csv>... > saida.json
O modelo antigo foi treinado com holdout/treino.csv + validacao.csv; só holdout/teste.csv (45 textos) é inédito para ele.
"""
import sys, json, re, unicodedata, numpy as np, pandas as pd
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
LAB=["Relacionamento","Financeiro","Phishing","Loja Falsa","Desinformação","Seguro"]
def norm(t): return re.sub(r"\s+"," ",unicodedata.normalize("NFKC",str(t)).lower().strip().strip('"'))
pool=pd.read_csv(sys.argv[1]); H=sys.argv[2]
vistos=set()
for n in("treino","validacao"): vistos|=set(pd.read_csv(f"{H}/{n}.csv",encoding="utf-8-sig").Mensagem.map(norm))
teste=set(pd.read_csv(f"{H}/teste.csv",encoding="utf-8-sig").Mensagem.map(norm))
pool["visto_no_treino_antigo"]=pool.Mensagem.map(norm).isin(vistos); pool["no_teste_antigo"]=pool.Mensagem.map(norm).isin(teste)
def met(y,p,rotulos=range(6)):
    pres=[i for i in rotulos if (np.array(y)==i).any()]
    r=classification_report(y,p,labels=list(range(6)),target_names=LAB,output_dict=True,zero_division=0)
    return {"n":len(y),"acc":round(accuracy_score(y,p),4),"f1_macro_classes_presentes":round(f1_score(y,p,labels=pres,average="macro",zero_division=0),4),
            "f1_por_classe":{LAB[i]:round(r[LAB[i]]["f1-score"],3) for i in range(6) if r[LAB[i]]["support"]>0},
            "n_por_classe":{LAB[i]:int(r[LAB[i]]["support"]) for i in range(6) if r[LAB[i]]["support"]>0},
            "matriz":confusion_matrix(y,p,labels=list(range(6))).tolist()}
out={"definicao":{"visto":"texto presente em treino/validação do modelo antigo (vazamento a favor dele)","inedito":"nunca visto: teste original de 45 textos, sintéticos e Telegram/Wpp"}}
for pf in sys.argv[3:]:
    pr=pd.read_csv(pf); m=pool.merge(pr[["linha_xlsx","pred","conf"]],on="linha_xlsx"); m["y"]=m.classe.map({c:i for i,c in enumerate(LAB)}); m["p"]=m.pred.map({c:i for i,c in enumerate(LAB)})
    r={}
    fb=m[m.facebook]
    r["facebook_todos(vazado)"]=met(fb.y,fb.p)
    r["facebook_inedito_p/o_modelo(teste original)"]=met(fb[fb.no_teste_antigo].y,fb[fb.no_teste_antigo].p) if fb.no_teste_antigo.any() else None
    r["facebook_Seguro_recall_vazado"]=round(float((fb[fb.classe=="Seguro"].y==fb[fb.classe=="Seguro"].p).mean()),3)
    r["por_fonte"]={f:{"n":len(g),"acc":round(float((g.y==g.p).mean()),3),"vazado":round(float(g.visto_no_treino_antigo.mean()),2)} for f,g in m.groupby("fonte")}
    ined=m[~m.visto_no_treino_antigo]; r["todos_inéditos_(teste45+Telegram)"]=met(ined[ined.tipo=="real"].y,ined[ined.tipo=="real"].p)
    syn=m[m.tipo=="sintético"]; r["sintéticos_diagnóstico(não é teste)"]=met(syn.y,syn.p)
    r["conf_media_acertos"]=round(float(m[m.y==m.p].conf.mean()),3); r["conf_media_erros"]=round(float(m[m.y!=m.p].conf.mean()),3)
    out[pf.split("/")[-1]]=r
print(json.dumps(out,ensure_ascii=False,indent=1))
