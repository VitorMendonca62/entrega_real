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
