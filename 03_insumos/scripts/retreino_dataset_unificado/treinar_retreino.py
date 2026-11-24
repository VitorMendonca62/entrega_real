"""Retreino do BERTimbau com o dataset unificado — mesmo pipeline das autoras (treinar_bert.py), com os splits de splits.json.
Hiperparâmetros idênticos: lr 2e-5, batch 16, 4 épocas, weight decay 0.01, max_length 512, seed 42, early stopping (paciência 2), melhor época por F1 macro.
Diferenças deliberadas (iguais para TODOS os braços, logo não enviesam a comparação):
  * a época é escolhida numa validação separada (10% do treino, só dados reais), e não no próprio teste (a causa do viés otimista admitido no artigo);
  * padding dinâmico em vez de padding="max_length" (matematicamente equivalente: atenção mascara o padding; mais rápido). --padding max_length volta ao original.
Uso (GPU): python treinar_retreino.py --dados dados_retreino --saida resultados --exp "fbcv_*" "loso_B_*" final_B
           python treinar_retreino.py --smoke      # teste rápido de ambiente (1 época, 48 exemplos)
É retomável: experimentos com resultado.json são pulados.
Determinismo: por padrão usa enable_full_determinism(42) (algoritmos determinísticos na GPU), para que a mesma GPU/versões
reproduzam os mesmos números. --sem-determinismo desliga (mais rápido, mas resultados podem variar na 3ª casa).
Diagnóstico de sintéticos: modelos que não viram nenhum sintético (braços A e C) também classificam os 210 sintéticos
(predicoes_sinteticos_diag.csv). Isso não é teste; serve só para medir a distância entre sintético e real.
"""
import os, sys, json, time, fnmatch, argparse, shutil, hashlib, platform
os.environ.setdefault("CUBLAS_WORKSPACE_CONFIG",":4096:8")   # precisa existir antes de o CUDA inicializar
import numpy as np, pandas as pd

ap=argparse.ArgumentParser()
ap.add_argument("--dados",default="dados_retreino"); ap.add_argument("--saida",default="resultados_retreino")
ap.add_argument("--exp",nargs="+",default=["fbcv_*","loso_B_*","loso_A_*","final_B"],help="nomes ou padrões (fnmatch) de splits.json")
ap.add_argument("--modelo",default="neuralmind/bert-base-portuguese-cased"); ap.add_argument("--padding",choices=["dinamico","max_length"],default="dinamico")
ap.add_argument("--smoke",action="store_true"); ap.add_argument("--listar",action="store_true")
ap.add_argument("--sem-determinismo",dest="determinismo",action="store_false")
a=ap.parse_args()

SEED=42; MAXLEN=512
LABELS=["Relacionamento","Financeiro","Phishing","Loja Falsa","Desinformação","Seguro"]
# nomes completos na MESMA ordem usada pelo plugin (classificador_bert.py LABELS 0..5) e pelo checkpoint publicado
FULL=["Golpes Baseados Em Relacionamento","Golpes de Ganho Financeiro Ilusório","Ataques de Phishing e Roubo de Dados",
      "Fraudes em Lojas Virtuais Falsas","Golpes de Desinformação Digital","Seguro"]
ID2LABEL={i:n for i,n in enumerate(FULL)}; LABEL2ID={n:i for i,n in ID2LABEL.items()}

pool=pd.read_csv(f"{a.dados}/pool_dedup.csv"); S=json.load(open(f"{a.dados}/splits.json")); assert S["labels"]==LABELS
by=pool.set_index("linha_xlsx")
nomes=[n for n in S["splits"] if any(fnmatch.fnmatch(n,p) for p in a.exp)]
if a.smoke: nomes=nomes[:1]
if a.listar: print("\n".join(f"{n}  {{{', '.join(f'{k}:{len(v)}' for k,v in S['splits'][n].items())}}}" for n in nomes)); sys.exit()
print(len(nomes),"experimentos:",nomes)

import torch
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix
from transformers import (AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer,
                          EarlyStoppingCallback, DataCollatorWithPadding, set_seed, enable_full_determinism)
semear=(lambda: enable_full_determinism(SEED)) if a.determinismo else (lambda: set_seed(SEED))
SINT=pool[pool.tipo=="sintético"].linha_xlsx.astype(int).tolist()
from datasets import Dataset as HFDataset

tok=AutoTokenizer.from_pretrained(a.modelo)
def ds_de(ids,limite=None):
    df=by.loc[ids]; 
    if limite: df=df.iloc[:limite]
    d=HFDataset.from_dict({"text":df.Mensagem.astype(str).tolist(),"labels":[int(x) for x in df.label]})
    kw=dict(truncation=True,max_length=MAXLEN); 
    if a.padding=="max_length": kw["padding"]="max_length"
    return d.map(lambda b:tok(b["text"],**kw),batched=True,remove_columns=["text"])

def compute_metrics(p):
    pr=np.argmax(p.predictions,-1); y=p.label_ids
    return {"f1_macro":round(f1_score(y,pr,average="macro",zero_division=0),4),"f1_weighted":round(f1_score(y,pr,average="weighted",zero_division=0),4),"accuracy":round(accuracy_score(y,pr),4)}

ARGS=dict(num_train_epochs=1 if a.smoke else 4,per_device_train_batch_size=16,per_device_eval_batch_size=16,learning_rate=2e-5,weight_decay=0.01,
          eval_strategy="epoch",save_strategy="epoch",load_best_model_at_end=True,metric_for_best_model="f1_macro",greater_is_better=True,
          logging_steps=10,seed=SEED,data_seed=SEED,report_to="none",save_total_limit=2,full_determinism=a.determinismo)
os.makedirs(a.saida,exist_ok=True)
meta={"torch":torch.__version__,"python":platform.python_version(),"gpu":torch.cuda.get_device_name(0) if torch.cuda.is_available() else None,
      "sha256_pool":hashlib.sha256(open(f"{a.dados}/pool_dedup.csv","rb").read()).hexdigest(),"sha256_splits":hashlib.sha256(open(f"{a.dados}/splits.json","rb").read()).hexdigest(),
      "args":ARGS,"padding":a.padding,"modelo_base":a.modelo,"determinismo":a.determinismo}
import transformers, datasets; meta["transformers"]=transformers.__version__; meta["datasets"]=datasets.__version__
json.dump(meta,open(f"{a.saida}/meta_execucao.json","w"),indent=1)

for n in nomes:
    d=f"{a.saida}/{n}"; 
    if os.path.exists(f"{d}/resultado.json") and not a.smoke: print("pulando",n); continue
    os.makedirs(d,exist_ok=True); sp=S["splits"][n]; t0=time.time(); lim=48 if a.smoke else None
    semear()
    model=AutoModelForSequenceClassification.from_pretrained(a.modelo,num_labels=6,id2label=ID2LABEL,label2id=LABEL2ID)
    dtr,dva=ds_de(sp["train"],lim),ds_de(sp["val"],lim)
    tr=Trainer(model=model,args=TrainingArguments(output_dir=f"{d}/ckpt",**ARGS),train_dataset=dtr,eval_dataset=dva,compute_metrics=compute_metrics,
               data_collator=DataCollatorWithPadding(tok),callbacks=[EarlyStoppingCallback(early_stopping_patience=2)])
    tr.train()
    hist=[h for h in tr.state.log_history if "eval_f1_macro" in h]
    res={"experimento":n,"n_treino":len(dtr),"n_val":len(dva),"n_teste":len(sp["test"]),"epocas_executadas":len(hist),
         "melhor_val_f1_macro":max(h["eval_f1_macro"] for h in hist),"historico_val":[{k:h[k] for k in("epoch","eval_loss","eval_f1_macro","eval_accuracy")} for h in hist]}
    if sp["test"]:
        ids=sp["test"][:lim] if lim else sp["test"]; dte=ds_de(ids); po=tr.predict(dte); pr=np.argmax(po.predictions,-1); y=po.label_ids
        pb=torch.softmax(torch.tensor(po.predictions),-1).numpy()
        out=pd.DataFrame({"linha_xlsx":ids,"y":y,"pred":pr,"conf":pb.max(1).round(4)}); 
        for i in range(6): out[f"p_{i}"]=pb[:,i].round(4)
        out.to_csv(f"{d}/predicoes.csv",index=False)
        pres=[i for i in range(6) if (y==i).any()]
        rep=classification_report(y,pr,labels=list(range(6)),target_names=LABELS,output_dict=True,zero_division=0)
        res.update({"acc":round(accuracy_score(y,pr),4),"f1_macro_classes_presentes":round(f1_score(y,pr,labels=pres,average="macro",zero_division=0),4),
                    "report":rep,"matriz":confusion_matrix(y,pr,labels=list(range(6))).tolist()})
    if sp["test"] and not (set(sp["train"])|set(sp["val"]))&set(SINT):   # diagnóstico, não é teste
        ids=SINT[:lim] if lim else SINT; po=tr.predict(ds_de(ids)); pb=torch.softmax(torch.tensor(po.predictions),-1).numpy()
        out=pd.DataFrame({"linha_xlsx":ids,"y":po.label_ids,"pred":pb.argmax(1),"conf":pb.max(1).round(4)}); out.to_csv(f"{d}/predicoes_sinteticos_diag.csv",index=False)
        res["sinteticos_diag_acc"]=round(float((out.y==out.pred).mean()),4)
    if n=="final_B" and not a.smoke:                    # modelo candidato no formato que o plugin carrega (pasta HF)
        md=f"{a.saida}/modelo_candidato"; tr.save_model(md); tok.save_pretrained(md)
        cfg=json.load(open(f"{md}/config.json")); assert [cfg["id2label"][str(i)] for i in range(6)]==FULL
    shutil.rmtree(f"{d}/ckpt",ignore_errors=True)
    res["segundos"]=round(time.time()-t0); json.dump(res,open(f"{d}/resultado.json","w"),ensure_ascii=False,indent=1)
    print(f"== {n}: acc={res.get('acc')} f1={res.get('f1_macro_classes_presentes')} val={res['melhor_val_f1_macro']} ({res['segundos']}s)",flush=True)
    del tr,model; torch.cuda.empty_cache() if torch.cuda.is_available() else None
print("fim")
