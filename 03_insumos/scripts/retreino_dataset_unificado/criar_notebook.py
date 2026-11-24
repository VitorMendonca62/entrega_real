"""Gera o notebook Colab do retreino (no padrão de Treinar_BERTimbau_VeritaPlugin_v3.ipynb) e o pacote que ele recebe.
Uso: python -I scripts/criar_notebook.py      (rodar dentro de retreino_dataset_unificado/)
Saídas: Retreino_BERTimbau_Unificado_Colab_v3.ipynb, pacote_colab_retreino.zip
"""
import json, hashlib, zipfile, pathlib

AQUI = pathlib.Path.cwd()
PACOTE = ["scripts/treinar_retreino.py", "scripts/comparar.py",
          "dados_retreino/pool_dedup.csv", "dados_retreino/splits.json", "dados_retreino/resumo_splits.json",
          "baseline/pred_plugin_publicado.csv", "baseline/pred_1a_execucao.csv", "baseline/pred_2a_execucao.csv"]
sha = lambda p: hashlib.sha256((AQUI / p).read_bytes()).hexdigest()
ESPERADO = {p: sha(p) for p in ("dados_retreino/pool_dedup.csv", "dados_retreino/splits.json")}

md = lambda s: {"cell_type": "markdown", "metadata": {}, "source": s.strip("\n").splitlines(True)}
code = lambda s: {"cell_type": "code", "metadata": {}, "execution_count": None, "outputs": [], "source": s.strip("\n").splitlines(True)}

cells = [
md("""
# VeritaPlugin — retreino do BERTimbau com o dataset unificado (GPU)
Mesmo ambiente e mesmos hiperparâmetros do `Treinar_BERTimbau_VeritaPlugin_v3.ipynb`; muda só o dado
(`BrScamsFacebook_Unificado_2.xlsx`, 756 linhas → 751 após remover duplicatas) e a avaliação.
Abra no Google Colab com GPU (T4 serve). Execute as células na ordem. Não é necessária chave da OpenAI.

**O que é treinado (33 ajustes, todos a partir de `neuralmind/bert-base-portuguese-cased`):**

| Etapa | Experimentos | Pergunta que responde |
|---|---|---|
| 1 | `fbcv_A_*`, `fbcv_B_*` (10) | O dataset novo (B) é melhor que o antigo (A) nas mensagens do Facebook? |
| 2 | `loso_*_Interno` (2) | Sem nenhuma mensagem do Facebook no treino, quanto cada um acerta no Facebook? |
| 3 | demais `loso_*` (15) | O modelo aprendeu o estilo da fonte em vez do golpe? |
| 4 | `fbcv_C_*` (5) | Os sintéticos ajudam ou atrapalham? (C = unificado sem sintéticos) |
| 5 | `final_B` (1) | Modelo candidato com todos os dados, no formato do plugin |

**Regras garantidas pelos splits (`dados_retreino/splits.json`, seed 42):** duplicatas removidas antes de separar;
teste só com mensagens do Facebook (ou uma fonte real inteira, no leave-one-source-out); sintéticos nunca no teste;
época escolhida numa validação de 10% tirada do treino (só dados reais), nunca no teste.

Preservamos batch 16, até 4 épocas, learning rate 2e-5, weight decay 0.01, 512 tokens, seed 42 e early stopping
com paciência 2. Determinismo completo ligado (`enable_full_determinism(42)`): na mesma GPU e versões, os números se repetem.
Duração estimada: 1,5 a 2,5 h numa T4 (a real fica registrada). Cada etapa é **retomável**: experimentos com
`resultado.json` são pulados. Para não perder nada se o Colab desconectar, ligue `USAR_DRIVE` na célula de pacote.
"""),
code("""
import sys, subprocess, pathlib, json, shutil, datetime, hashlib, os
print('Python do notebook:', sys.version)
if shutil.which('nvidia-smi') is None:
    raise RuntimeError('Ative uma GPU em Ambiente de execução > Alterar tipo de ambiente de execução antes de continuar.')
subprocess.run(['nvidia-smi'], check=True)
ROOT = pathlib.Path('/content/veritaplugin_bert')
ROOT.mkdir(exist_ok=True)
BOOTSTRAP = ROOT / 'uv_bootstrap'
# O kernel do Colab pode usar outra versão; o treinamento roda em Python 3.12 separado.
subprocess.run([sys.executable, '-m', 'pip', 'install', '--target', str(BOOTSTRAP),
                '--upgrade', 'uv==0.13.4'], check=True)
uv_env = os.environ.copy()
uv_env['PYTHONPATH'] = str(BOOTSTRAP)
uv_env['UV_PYTHON_INSTALL_DIR'] = str(ROOT / 'python_builds')
uv_env['UV_CACHE_DIR'] = str(ROOT / 'uv_cache')
VENV = ROOT / 'venv_py312'
PYTHON = str(VENV / 'bin/python')
if not VENV.exists():
    subprocess.run([sys.executable, '-m', 'uv', 'venv', '--python', '3.12',
                    '--managed-python', '--seed', str(VENV)], env=uv_env, check=True)
subprocess.run([PYTHON, '-c',
    'import sys; assert sys.version_info[:2] == (3,12); print("Python do treinamento:", sys.version)'], check=True)
(ROOT/'bootstrap_versoes.txt').write_text(
    'kernel: ' + sys.version + chr(10) +
    subprocess.check_output([PYTHON, '--version'], text=True) +
    subprocess.check_output([sys.executable, '-m', 'uv', '--version'], env=uv_env, text=True))
subprocess.run([PYTHON, '-m', 'pip', 'install', 'torch==2.4.0',
                '--index-url', 'https://download.pytorch.org/whl/cu121'], check=True)
subprocess.run([PYTHON, '-m', 'pip', 'install',
    'transformers==4.44.2', 'datasets==2.21.0', 'accelerate==0.34.2',
    'numpy==1.26.4', 'pandas==2.2.3', 'scikit-learn==1.5.2',
    'matplotlib==3.9.2', 'pyarrow==17.0.0', 'huggingface-hub==0.24.7'], check=True)
subprocess.run([PYTHON, '-c',
    'import torch; assert torch.cuda.is_available(); print(torch.__version__, torch.cuda.get_device_name(0))'], check=True)
"""),
md("""
## Pacote com código e dados fixados
Envie `pacote_colab_retreino.zip` quando o botão aparecer. Os hashes do dataset deduplicado e dos splits são
conferidos: se não baterem, o pacote não é o que foi analisado e a célula para.

`USAR_DRIVE = True` grava os resultados no seu Google Drive (`MyDrive/veritaplugin_retreino`). Se o Colab cair,
rode tudo de novo: as etapas pulam o que já terminou.
"""),
code(f"""
USAR_DRIVE = False
ESPERADO = {json.dumps(ESPERADO, indent=1)}
WORK = ROOT / 'retreino'
if USAR_DRIVE:
    from google.colab import drive
    drive.mount('/content/drive')
    WORK = pathlib.Path('/content/drive/MyDrive/veritaplugin_retreino')
WORK.mkdir(parents=True, exist_ok=True)
if not (WORK/'dados_retreino/splits.json').exists():
    from google.colab import files
    up = files.upload()            # escolha pacote_colab_retreino.zip
    nome = next(iter(up))
    shutil.unpack_archive(nome, WORK)
for p, h in ESPERADO.items():
    real = hashlib.sha256((WORK/p).read_bytes()).hexdigest()
    if real != h:
        raise RuntimeError(f'{{p}} não confere: {{real}} != {{h}}. Envie o pacote correto.')
RES = WORK / 'resultados_retreino'
RES.mkdir(exist_ok=True)
(RES/'requirements-lock.txt').write_text(subprocess.check_output([PYTHON,'-m','pip','freeze'],text=True))
shutil.copy2(ROOT/'bootstrap_versoes.txt', RES/'bootstrap_versoes.txt')
(RES/'gpu.txt').write_text(subprocess.check_output(['nvidia-smi'],text=True))
subprocess.run([PYTHON, 'scripts/treinar_retreino.py', '--listar', '--exp', '*'], cwd=WORK, check=True)
print('Pasta de trabalho:', WORK)
"""),
md("""
## Fixar a revisão do modelo base
Baixa `neuralmind/bert-base-portuguese-cased` numa revisão resolvida agora e registrada em `modelo_base.json`.
Todos os 33 ajustes partem desse mesmo snapshot local. O modelo publicado do plugin não é usado como ponto de partida.
"""),
code("""
preparacao = r'''
import pathlib, json, sys
from huggingface_hub import HfApi, snapshot_download
model = 'neuralmind/bert-base-portuguese-cased'
alvo = pathlib.Path(sys.argv[1])
if alvo.exists():
    print('já fixado:', alvo.read_text()); raise SystemExit
revision = HfApi().model_info(model).sha
snapshot = snapshot_download(model, revision=revision,
    allow_patterns=['config.json','tokenizer*','vocab.txt','special_tokens_map.json',
                    '*.safetensors','pytorch_model.bin'])
alvo.write_text(json.dumps({'repo_id':model,'revision':revision,'snapshot':snapshot},indent=2))
print(alvo.read_text())
'''
(ROOT/'preparar_modelo.py').write_text(preparacao)
subprocess.run([PYTHON, str(ROOT/'preparar_modelo.py'), str(RES/'modelo_base.json')], check=True)
modelo_base = json.loads((RES/'modelo_base.json').read_text())
if not pathlib.Path(modelo_base['snapshot']).is_dir():   # sessão nova com resultados no Drive: baixa a mesma revisão
    subprocess.run([PYTHON, '-c', 'from huggingface_hub import snapshot_download as s; import sys; '
                    'print(s(sys.argv[1], revision=sys.argv[2], allow_patterns=["config.json","tokenizer*","vocab.txt",'
                    '"special_tokens_map.json","*.safetensors","pytorch_model.bin"]))',
                    modelo_base['repo_id'], modelo_base['revision']], check=True)
MODELO = modelo_base['snapshot']
assert pathlib.Path(MODELO).is_dir(), MODELO
"""),
md("""
## Função de execução e teste rápido
`rodar(...)` chama o script de treino num subprocesso, mostra a saída ao vivo, acrescenta tudo em
`resultados_retreino/treinamento.log` e registra cada etapa em `status.json`. Uma falha para a célula.
O teste rápido (1 época, 48 exemplos, cerca de 1 minuto) confirma treino, predição e diagnóstico de sintéticos
antes das horas de GPU. Os números dele não significam nada.
"""),
code("""
import time
def rodar(etapa, *exp, saida=None, extra=()):
    saida = saida or RES
    status_f = RES/'status.json'
    status = json.loads(status_f.read_text()) if status_f.exists() else {}
    t0 = time.time()
    status[etapa] = {'inicio_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(), 'status': 'rodando'}
    status_f.write_text(json.dumps(status, indent=2))
    env = os.environ.copy(); env['PYTHONUNBUFFERED'] = '1'; env['MPLBACKEND'] = 'Agg'
    cmd = [PYTHON, 'scripts/treinar_retreino.py', '--modelo', MODELO, '--saida', str(saida), *extra]
    if exp: cmd += ['--exp', *exp]
    try:
        with (RES/'treinamento.log').open('a') as log:
            log.write(f'\\n===== {etapa} {datetime.datetime.now(datetime.timezone.utc).isoformat()}\\n')
            proc = subprocess.Popen(cmd, cwd=WORK, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
            try:
                for linha in proc.stdout:
                    log.write(linha); log.flush(); print(linha, end='')
                rc = proc.wait()
            except BaseException:
                proc.terminate()
                try: proc.wait(timeout=20)
                except subprocess.TimeoutExpired: proc.kill(); proc.wait()
                raise
        status[etapa].update(status='completa' if rc == 0 else 'falhou', returncode=rc)
        if rc != 0:
            raise RuntimeError(f'{etapa} falhou. Veja treinamento.log; rode a célula de novo para retomar.')
    except BaseException as exc:
        if status[etapa]['status'] == 'rodando': status[etapa].update(status='interrompida', erro=type(exc).__name__)
        raise
    finally:
        status[etapa]['segundos'] = round(time.time() - t0)
        status_f.write_text(json.dumps(status, indent=2))

rodar('smoke', saida=ROOT/'smoke_out', extra=('--smoke',))
"""),
md("## Etapa 1: Facebook-CV, braços A (dados originais) e B (unificado). Comparação principal (10 treinos)"),
code("rodar('etapa1_fbcv_AB', 'fbcv_A_*', 'fbcv_B_*')"),
md("## Etapa 2: leave-Interno-out, treino sem nenhuma mensagem do Facebook (2 treinos)"),
code("rodar('etapa2_loso_interno', 'loso_B_Interno', 'loso_A_Interno')"),
md("## Etapa 3: leave-one-source-out nas demais fontes (15 treinos)"),
code("rodar('etapa3_loso_fontes', 'loso_B_Externo*', 'loso_A_Externo*', 'loso_B_Telegram*')"),
md("## Etapa 4: ablação sem dados sintéticos, braço C (5 treinos)"),
code("rodar('etapa4_fbcv_C', 'fbcv_C_*')"),
md("""
## Etapa 5: modelo candidato (todos os dados; 1 treino)
Sai em `resultados_retreino/modelo_candidato/` no mesmo formato da pasta `modelo_bert` do plugin
(`config.json` com os mesmos rótulos 0..5, `model.safetensors`, tokenizer). **Não substitui nada**: só é
copiado para o plugin depois da comparação aprovada.
"""),
code("rodar('etapa5_final_B', 'final_B')"),
md("## Comparação (prévia) e download\nRode mesmo após uma falha, para preservar o log. Baixe antes que a sessão do Colab termine."),
code("""
subprocess.run([PYTHON, 'scripts/comparar.py', str(RES), 'dados_retreino', str(RES/'comparacao.md'), str(RES/'comparacao.json')], cwd=WORK)
if (RES/'comparacao.md').exists():
    from IPython.display import Markdown, display
    display(Markdown((RES/'comparacao.md').read_text()))
print((RES/'status.json').read_text() if (RES/'status.json').exists() else 'Treinamento não iniciado')
"""),
code("""
# zip leve: métricas, predições, logs e versões (sem os pesos)
import zipfile
from google.colab import files
leve = ROOT/'resultados_retreino_metricas.zip'
with zipfile.ZipFile(leve, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in RES.rglob('*'):
        if p.is_file() and 'modelo_candidato' not in p.parts:
            z.write(p, p.relative_to(RES))
files.download(str(leve))
if (RES/'modelo_candidato').is_dir():                 # cerca de 400 MB
    pesado = shutil.make_archive(str(ROOT/'modelo_candidato'), 'zip', root_dir=RES, base_dir='modelo_candidato')
    files.download(pesado)
"""),
]

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
      "language_info": {"name": "python"}, "colab": {"name": "Retreino_BERTimbau_Unificado_Colab_v3.ipynb"}, "accelerator": "GPU"},
      "nbformat": 4, "nbformat_minor": 0}
json.dump(nb, open(AQUI / "Retreino_BERTimbau_Unificado_Colab_v3.ipynb", "w"), ensure_ascii=False, indent=1)
with zipfile.ZipFile(AQUI / "pacote_colab_retreino.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for p in PACOTE: z.write(AQUI / p, p)
print("ok", ESPERADO)
