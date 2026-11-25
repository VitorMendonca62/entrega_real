"""Comparação pareada TF-IDF × BERTimbau no Facebook-CV (mesmas 60 mensagens, mesmos 5 folds).

Uso (a partir da raiz do repositório):
  python -I 03_insumos/scripts/tfidf_retreino/comparar_tfidf_bert.py

Entradas (já versionadas):
  BERT:   03_insumos/amostras/retreino_dataset_unificado/experimentos/fbcv_<braço>_f<k>/predicoes.csv
  TF-IDF: 03_insumos/amostras/tfidf_retreino/predicoes.csv (execução no Colab de 24/11/2026)
  Folds:  03_insumos/amostras/retreino_dataset_unificado/dados/splits.json

Confere que os folds do TF-IDF são idênticos aos do BERT antes de comparar.
Diferença de protocolo: o BERT treina com 'train' e escolhe a época em 'val' (10% só de reais);
o TF-IDF não tem época e treina com 'train' + 'val'. O teste é o mesmo.

Saída: 03_insumos/tabelas/tfidf_retreino/tfidf_vs_bert.csv e o resumo no terminal.
"""
import json, os, sys
import numpy as np, pandas as pd
from scipy.stats import binomtest

RAIZ = os.getcwd()
B = "03_insumos/amostras/retreino_dataset_unificado"
T = "03_insumos/amostras/tfidf_retreino/predicoes.csv"
SAIDA = "03_insumos/tabelas/tfidf_retreino/tfidf_vs_bert.csv"
L = ["Relacionamento", "Financeiro", "Phishing", "Loja Falsa", "Desinformação", "Seguro"]
REPS, SEED = 10000, 42


def f1_macro_lote(y, p, idx):
    """F1 macro (sobre as 6 classes, zero_division=0) para cada linha de índices de bootstrap."""
    yy, pp = y[idx], p[idx]
    f = []
    for c in range(len(L)):
        tp = ((yy == c) & (pp == c)).sum(1)
        fp = ((yy != c) & (pp == c)).sum(1)
        fn = ((yy == c) & (pp != c)).sum(1)
        den = 2 * tp + fp + fn
        f.append(np.where(den > 0, 2 * tp / np.maximum(den, 1), 0.0))
    return np.mean(f, axis=0)


splits = json.load(open(os.path.join(B, "dados/splits.json")))["splits"]
tf = pd.read_csv(T)
tf = tf[tf["avaliacao"] == "facebook_cv"]
folds_tf = {int(k): sorted(g["linha_xlsx"]) for k, g in tf[(tf.braco == "A") & (tf.modelo == "SVM")].groupby("fold")}
for k in range(1, 6):
    assert sorted(splits[f"fbcv_A_f{k}"]["test"]) == folds_tf[k], f"fold {k} diferente"
print("folds do TF-IDF idênticos aos do BERT: ok")

rng = np.random.default_rng(SEED)
idx = rng.integers(0, 60, size=(REPS, 60))
linhas = []
for braco in "ABC":
    bert = pd.concat([pd.read_csv(os.path.join(B, f"experimentos/fbcv_{braco}_f{k}/predicoes.csv")) for k in range(1, 6)])
    for mod in ["SVM", "LR"]:
        t = tf[(tf.braco == braco) & (tf.modelo == mod)][["linha_xlsx", "verdadeiro", "previsto"]]
        m = bert.merge(t, on="linha_xlsx")
        assert len(m) == 60 and (m["y"].map(lambda i: L[i]) == m["verdadeiro"]).all()
        y = m["y"].to_numpy()
        pb = m["pred"].to_numpy()
        pt = m["previsto"].map(L.index).to_numpy()
        ct, cb = pt == y, pb == y
        so_t, so_b = int((ct & ~cb).sum()), int((~ct & cb).sum())
        full = np.arange(60)[None, :]
        d = f1_macro_lote(y, pt, idx) - f1_macro_lote(y, pb, idx)
        linhas.append({
            "braco": braco, "tfidf": mod,
            "acertos_tfidf": int(ct.sum()), "acertos_bert": int(cb.sum()),
            "f1_macro_tfidf": float(f1_macro_lote(y, pt, full)[0]), "f1_macro_bert": float(f1_macro_lote(y, pb, full)[0]),
            "delta_f1_macro": float(f1_macro_lote(y, pt, full)[0] - f1_macro_lote(y, pb, full)[0]),
            "ic95_inf": float(np.percentile(d, 2.5)), "ic95_sup": float(np.percentile(d, 97.5)),
            "so_tfidf_acertou": so_t, "so_bert_acertou": so_b,
            "mcnemar_p_exato": float(binomtest(so_t, so_t + so_b).pvalue) if so_t + so_b else 1.0,
        })

r = pd.DataFrame(linhas)
r.to_csv(SAIDA, index=False)
pd.set_option("display.width", 200)
print(r.round(3).to_string(index=False))
print(f"gravado: {SAIDA}")
