"""Baixa um modelo da equipe do Hugging Face, na revisão registrada, e confere o sha256 de cada arquivo.
Uso (na pasta entrega_real):
  python3 -I 03_insumos/scripts/baixar_modelo_hf.py 03_insumos/modelos/bert_colab_holdout/modelo_download.json
  python3 -I 03_insumos/scripts/baixar_modelo_hf.py 03_insumos/modelos/retreino_dataset_unificado/modelo_download.json
  (opcional) segundo argumento: pasta de destino. Padrão: "destino_padrao" do JSON, relativo à pasta do JSON.
Só usa a biblioteca padrão. Arquivos já presentes e com o hash certo não são baixados de novo.
"""
import sys, json, hashlib, pathlib, urllib.request

if len(sys.argv) < 2:
    sys.exit(__doc__)
js = pathlib.Path(sys.argv[1]).resolve()
meta = json.loads(js.read_text())
dest = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else (js.parent/meta.get("destino_padrao", ".")).resolve()
dest.mkdir(parents=True, exist_ok=True)

def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""): h.update(b)
    return h.hexdigest()

ok = True
for r in meta["files"]:
    p = dest/r["file"]
    if not (p.exists() and sha256(p) == r["sha256"]):
        print("baixando", r["file"], r["bytes"], "bytes", flush=True)
        urllib.request.urlretrieve(r["url"], p)
    bom = p.stat().st_size == r["bytes"] and sha256(p) == r["sha256"]
    ok &= bom
    print(("ok   " if bom else "ERRO ") + r["file"])
if not ok:
    sys.exit("hash diferente do registrado: o arquivo baixado não é o modelo avaliado")
print("modelo conferido em", dest, "| repo", meta["repo_id"], "| revisão", meta["revision"])
