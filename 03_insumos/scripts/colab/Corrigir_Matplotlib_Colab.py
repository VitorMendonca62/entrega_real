# Execute esta célula no notebook Colab, antes de repetir a célula de treinamento.
import os, pathlib, datetime, subprocess, json

RUN = pathlib.Path('/content/veritaplugin_bert/execucao_20261020T193658592304Z')
PYTHON = '/content/veritaplugin_bert/venv_py312/bin/python'
log = RUN / 'treinamento.log'
if not log.is_file():
    raise RuntimeError('Não encontrei o log nessa pasta. Confira o caminho RUN.')
if (RUN / 'resultados_bert').exists():
    raise RuntimeError('Já existem resultados. Preserve a pasta e não reinicie por esta correção automática.')
texto_log = log.read_text(errors='replace')
if 'matplotlib_inline.backend_inline' not in texto_log or 'ValueError' not in texto_log:
    raise RuntimeError('O log não corresponde à falha de Matplotlib diagnosticada. Não alterei a tentativa.')

os.environ['MPLBACKEND'] = 'Agg'
os.environ['MPLCONFIGDIR'] = str(RUN / '.matplotlib')
(RUN / '.matplotlib').mkdir(exist_ok=True)
subprocess.run([PYTHON, '-c',
    'import matplotlib.pyplot as plt; import matplotlib; '
    'assert matplotlib.get_backend().lower() == "agg"; print("Matplotlib Agg OK")'],
    cwd=RUN, env=os.environ.copy(), check=True)

# Guardar a tentativa que falhou; não apagar nem sobrescrever os logs.
destino = RUN / ('falha_matplotlib_' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
destino.mkdir()
for nome in ['treinamento.log', 'status.json']:
    arquivo = RUN / nome
    if arquivo.exists():
        arquivo.rename(destino / nome)
(RUN / 'correcao_matplotlib.json').write_text(json.dumps({
    'backend': 'Agg', 'falha_anterior_preservada_em': str(destino),
    'motivo': 'Backend interativo do kernel Colab herdado pelo subprocesso isolado.'}, indent=2))
print('Falha anterior preservada em:', destino)
print('Agora execute novamente apenas a célula Executar os seis treinamentos.')
