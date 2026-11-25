"""Executa os dois experimentos TF-IDF e organiza tudo no padrão da entrega da replicação.

Uso (a partir desta pasta):
  python -I executar.py <saida_dir>

Etapas
  1. Ambiente: versões, sistema, pip freeze, hashes das entradas.
  2. tfidf_autoras_original: clona brunanoroes/Treinamento_TF-IDF-SVM no commit fixado e roda
     treinamento.py SEM alteração (sem rede, usa a cópia em autoras_original/ e registra isso).
  3. tfidf_retreino: roda rodar_tfidf.py (protocolo do relatório de retreino de 16/11/2026).
  4. Organiza logs/, ambiente/, tabelas/, amostras/ e grava manifesto_sha256.csv.

Estrutura gerada:
  logs/<experimento>/execucao.log   saída completa, com comando, início e fim
  logs/<experimento>/status.json    início, fim, duração, código de retorno
  logs/tfidf_retreino/treinos.jsonl um registro por treino (braço, modelo, fold, tamanhos, acertos)
  ambiente/                         proveniencia.json, entradas_sha256.json, sistema.json, requirements-lock.txt
  tabelas/                          métricas (JSON e CSV), comparações pareadas, matrizes de confusão
  amostras/                         predições por mensagem, folds do Facebook, linhas removidas na dedup
  manifesto_sha256.csv              hash de todos os arquivos gerados
"""
import sys, os, json, hashlib, platform, shutil, subprocess, time
from datetime import datetime, timezone

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.abspath(sys.argv[1])
REPO_URL = "https://github.com/brunanoroes/Treinamento_TF-IDF-SVM"
REPO_COMMIT = "a6d2d0ae0781c6d40d71fa20457d0d0de853a968"   # o mesmo da replicação de 20/10
DATASET = os.path.join(AQUI, "entrada", "BrScamsFacebook_Unificado_2.xlsx")
DATASET_SHA = "b5d896002737217c6465de7526aec8b1e976840143868007cca242b81b1e4014"


def agora():
    return datetime.now(timezone.utc).isoformat()


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def pasta(*p):
    d = os.path.join(SAIDA, *p)
    os.makedirs(d, exist_ok=True)
    return d


def rodar(nome, cmd, cwd):
    """Roda um comando, grava execucao.log e status.json em logs/<nome>/."""
    d = pasta("logs", nome)
    inicio, t0 = agora(), time.time()
    with open(os.path.join(d, "execucao.log"), "w") as log:
        log.write(f"# experimento: {nome}\n# início (UTC): {inicio}\n# diretório: {cwd}\n# comando: {' '.join(cmd)}\n\n")
        log.flush()
        r = subprocess.run(cmd, cwd=cwd, stdout=log, stderr=subprocess.STDOUT)
        fim = agora()
        log.write(f"\n# fim (UTC): {fim}\n# código de retorno: {r.returncode}\n# duração: {time.time() - t0:.1f}s\n")
    st = {"inicio_utc": inicio, "fim_utc": fim, "status": "completo" if r.returncode == 0 else "falhou",
          "codigo_retorno": r.returncode, "duracao_segundos": round(time.time() - t0, 1)}
    json.dump(st, open(os.path.join(d, "status.json"), "w"), indent=1)
    print(f"[{nome}] {st['status']} em {st['duracao_segundos']}s")
    if r.returncode != 0:
        sys.exit(f"falhou: veja {d}/execucao.log")
    return d


os.makedirs(SAIDA, exist_ok=True)
print(f"saída: {SAIDA}")

# ---------------- 1. ambiente ----------------
amb = pasta("ambiente")
assert sha(DATASET) == DATASET_SHA, "dataset diferente do usado no relatório de retreino"
import sklearn, numpy, pandas, scipy
json.dump({
    "registrado_utc": agora(), "python": platform.python_version(), "plataforma": platform.platform(),
    "processador": platform.processor() or platform.machine(), "cpus": os.cpu_count(),
    "colab": "COLAB_RELEASE_TAG" in os.environ or os.path.exists("/content"),
    "bibliotecas": {"scikit-learn": sklearn.__version__, "numpy": numpy.__version__,
                    "pandas": pandas.__version__, "scipy": scipy.__version__},
}, open(os.path.join(amb, "sistema.json"), "w"), indent=1)
with open(os.path.join(amb, "requirements-lock.txt"), "w") as f:
    subprocess.run([sys.executable, "-m", "pip", "freeze"], stdout=f, stderr=subprocess.DEVNULL)

# ---------------- 2. script original das autoras ----------------
trab = os.path.join(SAIDA, "_trabalho")
shutil.rmtree(trab, ignore_errors=True)
repo = os.path.join(trab, "Treinamento_TF-IDF-SVM")
origem = "github"
try:
    subprocess.run(["git", "clone", "-q", REPO_URL, repo], check=True, timeout=120)
    subprocess.run(["git", "-C", repo, "checkout", "-q", REPO_COMMIT], check=True)
    commit = subprocess.run(["git", "-C", repo, "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    data_commit = subprocess.run(["git", "-C", repo, "log", "-1", "--format=%cI"], capture_output=True, text=True).stdout.strip()
except Exception as e:
    print(f"sem acesso ao GitHub ({e}); usando a cópia em autoras_original/")
    origem, commit, data_commit = "copia_local_autoras_original", REPO_COMMIT + " (cópia, não verificado por git)", None
    shutil.copytree(os.path.join(AQUI, "autoras_original"), repo)
json.dump({
    "acesso_utc": agora(),
    "repositorios": [{"repo": "Treinamento_TF-IDF-SVM", "url": REPO_URL, "commit": commit,
                      "commit_date": data_commit, "origem": origem}],
    "dataset_unificado": {"arquivo": "BrScamsFacebook_Unificado_2.xlsx", "sha256": DATASET_SHA,
                          "origem": "planilha da equipe usada no relatório de retreino (16/11/2026)"},
}, open(os.path.join(amb, "proveniencia.json"), "w"), ensure_ascii=False, indent=1)

entradas = {
    "autoras/treinamento.py": sha(os.path.join(repo, "treinamento.py")),
    "autoras/BrScamsFacebook.xlsx": sha(os.path.join(repo, "BrScamsFacebook.xlsx")),
    "rodar_tfidf.py": sha(os.path.join(AQUI, "rodar_tfidf.py")),
    "executar.py": sha(os.path.abspath(__file__)),
    "entrada/BrScamsFacebook_Unificado_2.xlsx": sha(DATASET),
}
json.dump(entradas, open(os.path.join(amb, "entradas_sha256.json"), "w"), indent=1)

rodar("tfidf_autoras_original", [sys.executable, "-I", "treinamento.py"], cwd=repo)

# ---------------- 3. protocolo do retreino ----------------
res = os.path.join(trab, "resultados")
os.makedirs(res)
d = rodar("tfidf_retreino", [sys.executable, "-I", os.path.join(AQUI, "rodar_tfidf.py"), DATASET, res], cwd=AQUI)

# ---------------- 4. organizar ----------------
shutil.move(os.path.join(res, "treinos.jsonl"), os.path.join(d, "treinos.jsonl"))
for n in ["metricas.json", "tabela_facebook_cv.csv", "tabela_loso.csv", "tabela_pareadas.csv", "matrizes_facebook_cv.csv"]:
    shutil.move(os.path.join(res, n), os.path.join(pasta("tabelas"), n))
for n in ["predicoes.csv", "folds_facebook.csv", "dedup_removidas.csv"]:
    shutil.move(os.path.join(res, n), os.path.join(pasta("amostras"), n))
shutil.rmtree(trab)

linhas = ["arquivo,bytes,sha256"]
for raiz, _, arqs in os.walk(SAIDA):
    for a in sorted(arqs):
        p = os.path.join(raiz, a)
        rel = os.path.relpath(p, SAIDA)
        if rel != "manifesto_sha256.csv":
            linhas.append(f"{rel},{os.path.getsize(p)},{sha(p)}")
with open(os.path.join(SAIDA, "manifesto_sha256.csv"), "w") as f:
    f.write("\n".join([linhas[0]] + sorted(linhas[1:])) + "\n")
print(f"pronto: {len(linhas) - 1} arquivos em {SAIDA}")
