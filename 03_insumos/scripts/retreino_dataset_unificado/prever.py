"""Roda um modelo BERT já treinado (pasta HF) sobre o dataset anotado e grava as predições.
Uso: python -I prever.py <pasta_modelo> <dataset_anotado.csv> <saida.csv> [threads]
"""
import sys, time, numpy as np, pandas as pd, torch, torch.nn.functional as F
from transformers import AutoTokenizer, BertForSequenceClassification
mdir, src, out = sys.argv[1:4]; torch.set_num_threads(int(sys.argv[4]) if len(sys.argv)>4 else 4)
tok=AutoTokenizer.from_pretrained(mdir); m=BertForSequenceClassification.from_pretrained(mdir).eval()
id2=m.config.id2label; d=pd.read_csv(src)
txt=[str(t).strip().strip('"') if False else str(t) for t in d.Mensagem]
enc_len=[len(tok(t,truncation=True,max_length=512)["input_ids"]) for t in txt]
order=np.argsort(enc_len); P=np.zeros((len(d),len(id2)),dtype=np.float32); t0=time.time(); B=4
with torch.inference_mode():
    for k in range(0,len(order),B):
        ix=order[k:k+B]; b=tok([txt[i] for i in ix],return_tensors="pt",truncation=True,max_length=512,padding=True)
        P[ix]=F.softmax(m(**b).logits,-1).numpy()
        if (k//B)%25==0: print(k,len(order),round(time.time()-t0),flush=True)
o=d[["linha_xlsx","fonte","classe","tipo","facebook"]].copy()
o["pred"]=[id2[int(i)].replace("Golpes Baseados Em Relacionamento","Relacionamento").replace("Golpes de Ganho Financeiro Ilusório","Financeiro").replace("Ataques de Phishing e Roubo de Dados","Phishing").replace("Fraudes em Lojas Virtuais Falsas","Loja Falsa").replace("Golpes de Desinformação Digital","Desinformação") for i in P.argmax(1)]
o["conf"]=P.max(1).round(4)
for i in range(P.shape[1]): o[f"p_{i}"]=P[:,i].round(4)
o.to_csv(out,index=False); print("ok",round(time.time()-t0),"s")
