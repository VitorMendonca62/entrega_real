# Registro de comandos e ocorrências

Data da execução: 20/10/2026. Este é um índice reconstruído a partir dos comandos efetivamente executados, não uma captura de terminal contínua. Logs separados contêm as saídas originais disponíveis.

## Aquisição e preparação

- `git clone --depth 1 https://github.com/brunanoroes/<repo> outputs/evidencias/autores/<repo>` para os seis repositórios em `proveniencia.json`.
- Python `urllib.request` para página editorial, PDF pela rota download, metadados Hugging Face, model card e página Kaggle.
- `pdftotext -layout outputs/evidencias/autores/artigo.pdf work/artigo.txt`.
- `pdftoppm -f 11 -l 11 -scale-to 1500 -png -singlefile ...` para conferir a Figura 3.
- `python3 -m venv work/venv`.
- Instalação de bibliotecas e pins, conforme `instalacao.log` e `requirements-lock.txt`.

Tentativa inicial com `python` falhou (executável não disponível). Foi usado `python3`. Clone/download no ambiente com rede restrita falharam por resolução DNS; fora da restrição, os seis clones e os downloads públicos concluíram. A criação de servidor HTTP no ambiente com rede restrita retornou `PermissionError`; fora da restrição funcionou em loopback.

## Experimentos

- `work/venv/bin/python outputs/evidencias/scripts/replicar_cpu.py > outputs/evidencias/execucao/replicar_cpu.log 2>&1`
- `python3 outputs/evidencias/scripts/baixar_modelo.py > outputs/evidencias/execucao/modelo_download.log 2>&1`
- Cópia de `api.py`, `classificador_bert.py`, `pipeline_rag.py`, `base_conhecimento.py` para `work/api_local`, sem alterar conteúdo.
- `work/venv/bin/python outputs/evidencias/scripts/testar_local.py`: primeira tentativa produziu inferências/filtro e ficou bloqueada no TestClient; interrompida. A execução definitiva abaixo substituiu esses resultados.
- `HF_HOME="$PWD/work/hf_cache" timeout 60 work/venv/bin/python outputs/evidencias/scripts/testar_local.py > outputs/evidencias/execucao/testar_local.log 2>&1`: concluída, fora da restrição de sockets, sem chave e com HF offline.
- `work/venv/bin/python outputs/evidencias/scripts/auditoria_complementar.py`
- `work/venv/bin/python outputs/evidencias/scripts/graficos.py`
- `work/venv/bin/python outputs/evidencias/scripts/preparar_extensao_local.py`
- Uvicorn original iniciado com `env -u OPENAI_API_KEY HF_HUB_OFFLINE=1 OMP_NUM_THREADS=2 ../venv/bin/python -m uvicorn api:app --host 127.0.0.1 --port 8080` dentro de `work/api_local`.
- Três requisições urllib locais (mesmo código preservado em `testar_http.py`): respostas 200/400/401, gravadas em `api_http.json`.
- `python3 -m http.server 5500 --bind 127.0.0.1 --directory outputs/evidencias/autores/ReplicaTesteFacebook`: réplica aberta no navegador; captura real preservada.

Ambos os servidores foram encerrados normalmente ao final. Nenhuma API paga foi chamada. Nenhum treinamento BERT foi iniciado. Não houve instalação da extensão em navegador.

## Apresentação

Criação e revisão visual dos slides. Quinze slides renderizados; rótulos do gráfico e incorporação da imagem foram corrigidos após inspeção. Exportação final para PPTX, com 15 notas e 1 gráfico nativo. Inspeção estrutural do pacote PPTX passou. A apresentação não foi aberta no aplicativo Microsoft PowerPoint.
