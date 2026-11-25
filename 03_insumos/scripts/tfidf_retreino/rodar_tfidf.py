"""Linha de base TF-IDF no dataset unificado, com o mesmo protocolo do relatório de retreino (16/11/2026).

Uso:
  python -I rodar_tfidf.py <BrScamsFacebook_Unificado_2.xlsx> <saida_dir>

Modelos (sem nenhum ajuste de hiperparâmetro):
  SVM = configuração das autoras (repositório brunanoroes/Treinamento_TF-IDF-SVM):
        TfidfVectorizer(max_features=10000, ngram_range=(1,2), sublinear_tf=True)
        + LinearSVC(C=1.0, max_iter=2000, random_state=42)
  LR  = mesmo TF-IDF + LogisticRegression(class_weight="balanced"), que dá probabilidades.

Avaliações (iguais às do relatório):
  1. Facebook-CV: as 60 mensagens do Facebook em 5 folds estratificados (semente 42);
     cada uma testada uma vez, por modelos que não a viram. Braços A, B e C.
  2. Leave-one-source-out: cada fonte real fica inteira fora do treino. Braços A e B.
  3. Comparações pareadas B−A, C−A, B−C: McNemar exato e IC 95% bootstrap do ΔF1 macro.

Saídas: metricas.json, predicoes.csv (uma linha por mensagem × braço × modelo), log no terminal.
"""
import sys, json, re, unicodedata, hashlib, platform, time
import numpy as np, pandas as pd, sklearn, scipy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, accuracy_score, confusion_matrix
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.csgraph import connected_components
from scipy.sparse import csr_matrix
from scipy.stats import binomtest

XLSX, OUT = sys.argv[1], sys.argv[2]
SEED = 42
SINT, TELE, FB = "Dados Sintéticos", "Telegram/Wpp Dataset", "Interno"
CURTO = {
    "Golpes Baseados Em Relacionamento": "Relacionamento",
    "Golpes de Ganho Financeiro Ilusório": "Financeiro",
    "Ataques de Phishing e Roubo de Dados": "Phishing",
    "Fraudes em Lojas Virtuais Falsas": "Loja Falsa",
    "Golpes de Desinformação Digital": "Desinformação",
    "Seguro": "Seguro",
}
ORDEM = ["Relacionamento", "Financeiro", "Phishing", "Loja Falsa", "Desinformação", "Seguro"]

t0 = time.time()
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] início")
print(f"python {platform.python_version()} | sklearn {sklearn.__version__} | numpy {np.__version__} "
      f"| pandas {pd.__version__} | scipy {scipy.__version__} | {platform.platform()}")
print(f"dataset {XLSX} sha256 {hashlib.sha256(open(XLSX, 'rb').read()).hexdigest()}")

# ---------------- dados e deduplicação (critério do relatório) ----------------
df = pd.read_excel(XLSX, sheet_name=0)
df["linha_xlsx"] = np.arange(len(df)) + 2
df["texto"] = df["Mensagem"].astype(str)
df["classe"] = df["Categoria"].map(CURTO)
df["fonte"] = df["Dataset"].astype(str).str.strip()
df["original"] = df["linha_xlsx"] <= 451
assert df["classe"].notna().all()


def norm(t):
    return re.sub(r"\s+", " ", unicodedata.normalize("NFKC", t).lower()).strip()


df["norm"] = df["texto"].map(norm)
v = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)).fit(df["norm"])
S = cosine_similarity(v.transform(df["norm"]))
np.fill_diagonal(S, 0)
nv = df["norm"].to_numpy(dtype=object)
adj = (S >= 0.85) | (nv[:, None] == nv[None, :])
np.fill_diagonal(adj, False)
_, df["grupo"] = connected_components(csr_matrix(adj), directed=False)
manter = (~df["texto"].str.strip().str.match(r"^https?://\S+$")).copy()
for _, sub in df[manter].groupby("grupo"):
    if len(sub) > 1:
        manter[sub.index if sub["classe"].nunique() > 1 else sub.index[1:]] = False
pool = df[manter].copy()
print(f"linhas: {len(df)} | após deduplicação: {len(pool)} | removidas (linha xlsx): "
      f"{df.loc[~manter, 'linha_xlsx'].tolist()}")
assert len(pool) == 751


def modelo(nome):
    tf = TfidfVectorizer(max_features=10000, ngram_range=(1, 2), sublinear_tf=True)
    clf = (LinearSVC(C=1.0, max_iter=2000, random_state=SEED) if nome == "SVM"
           else LogisticRegression(max_iter=2000, class_weight="balanced", random_state=SEED))
    return Pipeline([("tfidf", tf), ("clf", clf)])


def braco(nome, base):
    return {"A": base[base["original"]], "B": base, "C": base[base["fonte"] != SINT]}[nome]


def metricas(y, p):
    y, p = np.asarray(y), np.asarray(p)
    gy, gp, seg = y != "Seguro", p != "Seguro", y == "Seguro"
    return {
        "n": int(len(y)),
        "acuracia": float(accuracy_score(y, p)),
        "f1_macro": float(f1_score(y, p, labels=[c for c in ORDEM if c in set(y)], average="macro", zero_division=0)),
        "f1_seguro": float(f1_score(y, p, labels=["Seguro"], average="macro", zero_division=0)) if seg.any() else None,
        "alarme_falso": float(gp[seg].mean()) if seg.any() else None,
        "golpe_perdido": float((~gp)[gy].mean()) if gy.any() else None,
        "matriz": confusion_matrix(y, p, labels=ORDEM).tolist(),
    }


linhas = []
treinos = []


def treinar(nome, tr, teste, rotulo):
    t = time.time()
    m = modelo(nome).fit(tr["texto"], tr["classe"])
    p = prever(m, teste, rotulo)
    treinos.append({**rotulo, "n_treino": int(len(tr)), "n_teste": int(len(teste)),
                    "treino_por_fonte": tr["fonte"].value_counts().to_dict(),
                    "acertos": int((p == teste["classe"].values).sum()),
                    "segundos": round(time.time() - t, 2), "fim": time.strftime("%Y-%m-%dT%H:%M:%S")})
    return p


def prever(m, teste, rotulo):
    p = m.predict(teste["texto"])
    sc = m.decision_function(teste["texto"]) if rotulo["modelo"] == "SVM" else m.predict_proba(teste["texto"])
    cls = list(m.classes_)
    for (i, r), pi, s in zip(teste.iterrows(), p, sc):
        d = {**rotulo, "linha_xlsx": r["linha_xlsx"], "fonte": r["fonte"], "verdadeiro": r["classe"], "previsto": pi}
        d.update({f"score_{c}": round(float(s[cls.index(c)]), 6) for c in ORDEM})
        linhas.append(d)
    return p


res = {"ambiente": {"python": platform.python_version(), "sklearn": sklearn.__version__,
                    "numpy": np.__version__, "pandas": pd.__version__}}

# ---------------- 1. Facebook-CV ----------------
fb = pool[pool["fonte"] == FB]
cv = StratifiedKFold(5, shuffle=True, random_state=SEED)
folds = list(cv.split(fb, fb["classe"]))
print("\n== Facebook-CV (60 mensagens, 5 folds) ==")
for k, (_, te) in enumerate(folds, 1):
    print(f"fold {k}: linhas xlsx {sorted(fb['linha_xlsx'].iloc[te].tolist())}")
pred = {}
for k, (_, te) in enumerate(folds, 1):
    teste = fb.iloc[te]
    base = pool.drop(index=teste.index)
    for b in "ABC":
        tr = braco(b, base)
        for mn in ["SVM", "LR"]:
            p = treinar(mn, tr, teste, {"avaliacao": "facebook_cv", "braco": b, "modelo": mn, "fold": k})
            pred.setdefault((b, mn), {}).update(dict(zip(teste.index, p)))
            print(f"  fold {k} braço {b} {mn}: treino {len(tr)}, acertos {int((p == teste['classe'].values).sum())}/{len(teste)}")
res["facebook_cv"] = {}
ordem_idx = fb.index.tolist()
yfb = fb["classe"].values
for (b, mn), d in pred.items():
    res["facebook_cv"][f"{b}-{mn}"] = metricas(yfb, [d[i] for i in ordem_idx])

# comparações pareadas
rng = np.random.default_rng(SEED)
boot = rng.integers(0, len(yfb), size=(10000, len(yfb)))
res["pareadas"] = {}
for mn in ["SVM", "LR"]:
    for x, y in [("B", "A"), ("C", "A"), ("B", "C")]:
        px = np.array([pred[(x, mn)][i] for i in ordem_idx])
        py = np.array([pred[(y, mn)][i] for i in ordem_idx])
        cx, cy = px == yfb, py == yfb
        b_, c_ = int((cx & ~cy).sum()), int((~cx & cy).sum())
        p_mc = binomtest(b_, b_ + c_, 0.5).pvalue if b_ + c_ else 1.0
        f = lambda yy, pp: f1_score(yy, pp, labels=ORDEM, average="macro", zero_division=0)
        deltas = [f(yfb[s], px[s]) - f(yfb[s], py[s]) for s in boot]
        res["pareadas"][f"{mn} {x}-{y}"] = {
            "delta_acuracia": float(cx.mean() - cy.mean()),
            "delta_f1_macro": float(f(yfb, px) - f(yfb, py)),
            "ic95": [float(np.percentile(deltas, 2.5)), float(np.percentile(deltas, 97.5))],
            "mcnemar_b_c": [b_, c_], "p_exato": float(p_mc),
        }

# ---------------- 2. Leave-one-source-out ----------------
print("\n== Leave-one-source-out ==")
res["loso"] = {}
for fonte in sorted(pool["fonte"].unique()):
    if fonte == SINT:
        continue
    teste = pool[pool["fonte"] == fonte]
    base = pool[pool["fonte"] != fonte]
    for b in "AB":
        tr = braco(b, base)
        for mn in ["SVM", "LR"]:
            p = treinar(mn, tr, teste, {"avaliacao": "loso", "braco": b, "modelo": mn, "fold": fonte})
            res["loso"][f"{fonte}|{b}-{mn}"] = metricas(teste["classe"], p)
            print(f"  fora: {fonte:22s} braço {b} {mn}: acurácia {res['loso'][f'{fonte}|{b}-{mn}']['acuracia']:.3f}")

# ---------------- saída ----------------
pd.DataFrame(linhas).to_csv(f"{OUT}/predicoes.csv", index=False)
json.dump(res, open(f"{OUT}/metricas.json", "w"), ensure_ascii=False, indent=1)
with open(f"{OUT}/treinos.jsonl", "w") as fh:
    for t in treinos:
        fh.write(json.dumps(t, ensure_ascii=False) + "\n")
pd.DataFrame([{"linha_xlsx": fb["linha_xlsx"].iloc[i], "classe": fb["classe"].iloc[i], "fold": k}
              for k, (_, te) in enumerate(folds, 1) for i in te]).to_csv(f"{OUT}/folds_facebook.csv", index=False)
pd.DataFrame(removidas := df.loc[~manter, ["linha_xlsx", "fonte", "classe"]]).to_csv(f"{OUT}/dedup_removidas.csv", index=False)
tab = lambda d: pd.DataFrame([{"chave": k, **{a: b for a, b in v.items() if a != "matriz"}} for k, v in d.items()])
tab(res["facebook_cv"]).to_csv(f"{OUT}/tabela_facebook_cv.csv", index=False)
tab(res["loso"]).to_csv(f"{OUT}/tabela_loso.csv", index=False)
pd.DataFrame([{"comparacao": k, "delta_acuracia": v["delta_acuracia"], "delta_f1_macro": v["delta_f1_macro"],
               "ic95_inf": v["ic95"][0], "ic95_sup": v["ic95"][1], "mcnemar_b": v["mcnemar_b_c"][0],
               "mcnemar_c": v["mcnemar_b_c"][1], "p_exato": v["p_exato"]} for k, v in res["pareadas"].items()]
             ).to_csv(f"{OUT}/tabela_pareadas.csv", index=False)
pd.DataFrame([{"chave": k, "verdadeiro": ORDEM[i], **dict(zip(ORDEM, row))}
              for k, v in res["facebook_cv"].items() for i, row in enumerate(v["matriz"])]
             ).to_csv(f"{OUT}/matrizes_facebook_cv.csv", index=False)

print("\n== RESUMO Facebook-CV ==")
print(f"{'braço-modelo':10s} {'acur':>6s} {'F1mac':>6s} {'F1Seg':>6s} {'alarme':>7s} {'perdido':>7s}")
for k, r in res["facebook_cv"].items():
    print(f"{k:10s} {r['acuracia']:6.3f} {r['f1_macro']:6.3f} {r['f1_seguro']:6.3f} {r['alarme_falso']:7.2f} {r['golpe_perdido']:7.2f}")
print("\n== Pareadas (mesmas 60 mensagens) ==")
for k, r in res["pareadas"].items():
    print(f"{k:10s} Δacur {r['delta_acuracia']:+.3f} ΔF1 {r['delta_f1_macro']:+.3f} "
          f"[{r['ic95'][0]:+.2f}, {r['ic95'][1]:+.2f}] McNemar {r['mcnemar_b_c'][0]}/{r['mcnemar_b_c'][1]} p={r['p_exato']:.3f}")
for n in ["predicoes.csv", "metricas.json"]:
    print(f"{n} sha256 {hashlib.sha256(open(f'{OUT}/{n}', 'rb').read()).hexdigest()}")
print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] fim ({time.time() - t0:.0f}s)")
