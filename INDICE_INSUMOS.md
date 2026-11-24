# Índice de insumos da replicação

Gerado automaticamente a partir do manifesto.
Coluna *origem*: quem produziu o arquivo. Hashes completos em `03_insumos/tabelas/_controle/manifesto_sha256.csv`.

## Resumo por pasta e origem

| Pasta | Origem | Arquivos | Tamanho |
|---|---|---:|---:|
| 01_apresentacao | Equipe – documento ou código | 3 | 0.23 MB |
| 02_relatorios | Equipe – documento ou código | 5 | 0.02 MB |
| 02_relatorios | Equipe – produzido na execução | 1 | 0.00 MB |
| 02_relatorios | Equipe – corrigido na revisão | 4 | 0.05 MB |
| 04_materiais_autoras | Material das autoras (não produzido pela equipe) | 362 | 64.37 MB |
| 04_materiais_autoras | Derivado do artigo das autoras | 2 | 0.43 MB |
| LEIA-ME.md | Escrito na revisão | 1 | 0.01 MB |
| ambiente | Equipe – documento ou código | 2 | 0.00 MB |
| ambiente | Equipe – produzido na execução | 16 | 0.02 MB |
| amostras | Equipe – produzido na execução | 438 | 7.25 MB |
| imagens | Equipe – produzido na execução | 25 | 3.56 MB |
| imagens | Gerado na revisão a partir dos dados da execução | 7 | 0.48 MB |
| logs | Equipe – produzido na execução | 22 | 0.19 MB |
| logs | Escrito na revisão | 1 | 0.01 MB |
| modelos | Equipe – produzido na execução | 9 | 436.63 MB |
| scripts | Equipe – documento ou código | 10 | 0.35 MB |
| scripts | Equipe – produzido na execução | 5 | 0.04 MB |
| tabelas | Equipe – produzido na execução | 57 | 0.19 MB |
| tabelas | Gerado na revisão a partir dos dados da execução | 15 | 0.03 MB |
| tabelas | Escrito na revisão | 2 | 0.25 MB |

## Logs de execução (`03_insumos/logs/`)

| Arquivo | Origem | Bytes |
|---|---|---:|
| `logs/ambiente_e_proveniencia/instalacao.log` | Equipe – produzido na execução | 19431 |
| `logs/api_e_replica/replica_http.log` | Equipe – produzido na execução | 317 |
| `logs/baseline_investigacao_divergencia/150.log` | Equipe – produzido na execução | 1977 |
| `logs/baseline_investigacao_divergencia/151.log` | Equipe – produzido na execução | 1977 |
| `logs/baseline_investigacao_divergencia/152_original.log` | Equipe – produzido na execução | 1977 |
| `logs/baseline_tfidf_svm/baseline_original.log` | Equipe – produzido na execução | 1977 |
| `logs/baseline_tfidf_svm/replicar_cpu.log` | Equipe – produzido na execução | 5902 |
| `logs/bert_checkpoint_publicado/modelo_download.log` | Equipe – produzido na execução | 93 |
| `logs/bert_checkpoint_publicado/testar_local.log` | Equipe – produzido na execução | 472 |
| `logs/bert_treinamento_colab/falha_matplotlib_20261020T200039361303Z/status.json` | Equipe – produzido na execução | 184 |
| `logs/bert_treinamento_colab/falha_matplotlib_20261020T200039361303Z/treinamento.log` | Equipe – produzido na execução | 912 |
| `logs/bert_treinamento_colab/status.json` | Equipe – produzido na execução | 140 |
| `logs/bert_treinamento_colab/treinamento.log` | Equipe – produzido na execução | 84198 |
| `logs/controle_execucao/politica_final.json` | Equipe – produzido na execução | 18 |
| `logs/controle_execucao/politica_validacao.json` | Equipe – produzido na execução | 18 |
| `logs/controle_execucao/pptx_integridade.json` | Equipe – produzido na execução | 314 |
| `logs/controle_execucao/resumo_final_stdout.json` | Equipe – produzido na execução | 3004 |
| `logs/controle_execucao/verificacao_entrega_validacao.json` | Equipe – produzido na execução | 178 |
| `logs/dados_auditoria/auditoria_complementar.log` | Equipe – produzido na execução | 3698 |
| `logs/dados_auditoria/preparacao_original.log` | Equipe – produzido na execução | 6991 |
| `logs/extensao_integrada_checkpoint_publicado/reservas.jsonl` | Equipe – produzido na execução | 980 |
| `logs/gpt4o_v1_v2_v3/reservas.jsonl` | Equipe – produzido na execução | 59568 |
| `logs/revisao/reexecucao_baseline_layout_restaurado.log` | Escrito na revisão | 6034 |

## Amostras: splits, predições, entradas/saídas GPT, páginas de teste (`03_insumos/amostras/`)

| Arquivo | Origem | Bytes |
|---|---|---:|
| `amostras/baseline_investigacao_divergencia/150_predicoes.csv` | Equipe – produzido na execução | 32218 |
| `amostras/baseline_investigacao_divergencia/151_predicoes.csv` | Equipe – produzido na execução | 32218 |
| `amostras/baseline_investigacao_divergencia/152_original_predicoes.csv` | Equipe – produzido na execução | 32218 |
| `amostras/baseline_investigacao_divergencia/folds_bert_texto_original_predicoes.csv` | Equipe – produzido na execução | 30447 |
| `amostras/baseline_investigacao_divergencia/strip_mesmos_folds_predicoes.csv` | Equipe – produzido na execução | 30512 |
| `amostras/baseline_tfidf_svm/baseline_predicoes.csv` | Equipe – produzido na execução | 59785 |
| `amostras/baseline_tfidf_svm/exemplos_para_inspecao.json` | Equipe – produzido na execução | 2951 |
| `amostras/bert_treinamento_colab/` (30 arquivos; ver manifesto) | Equipe – produzido na execução | 2274160 |
| `amostras/dados_splits_regenerados/` (29 arquivos; ver manifesto) | Equipe – produzido na execução | 2267418 |
| `amostras/extensao_integrada_bert_colab/casos_integracao.json` | Equipe – produzido na execução | 4972 |
| `amostras/extensao_integrada_bert_colab/integracao_colab/15ca30c43269acb749153f6c336fcf4a65012c88070aa7b58aaaecab7f62e0a6.json` | Equipe – produzido na execução | 1132 |
| `amostras/extensao_integrada_bert_colab/integracao_colab/1fc06885543df485dca7f379e520d682d2f63e628ea83ee65812500a441ba1ae.json` | Equipe – produzido na execução | 1541 |
| `amostras/extensao_integrada_bert_colab/integracao_colab/2aabd796893fbf4d33572079a5b59e25a51b3b091b49d275b41528ddd1816efd.json` | Equipe – produzido na execução | 1209 |
| `amostras/extensao_integrada_bert_colab/integracao_colab/7a1928c2cab2badfae1688efd7a8393325c187372df79ece80113ed12acb7f3e.json` | Equipe – produzido na execução | 698 |
| `amostras/extensao_integrada_bert_colab/integracao_colab/b64cd5fb32fa25ab0f6893aa21376673b0a5e3b99fae7e11bb0fcda9e92555f6.json` | Equipe – produzido na execução | 1248 |
| `amostras/extensao_integrada_bert_colab/integracao_colab/c5abd04ed9474746a871631b41129feaedbed16109543594d293bbfae3d610da.json` | Equipe – produzido na execução | 1188 |
| `amostras/extensao_integrada_bert_colab/validacao_integracao.html` | Equipe – produzido na execução | 1650 |
| `amostras/extensao_integrada_checkpoint_publicado/casos.json` | Equipe – produzido na execução | 4308 |
| `amostras/extensao_integrada_checkpoint_publicado/gpt_00.json` | Equipe – produzido na execução | 11288 |
| `amostras/extensao_integrada_checkpoint_publicado/gpt_01.json` | Equipe – produzido na execução | 10468 |
| `amostras/extensao_integrada_checkpoint_publicado/gpt_02.json` | Equipe – produzido na execução | 7323 |
| `amostras/extensao_integrada_checkpoint_publicado/gpt_03.json` | Equipe – produzido na execução | 10259 |
| `amostras/extensao_integrada_checkpoint_publicado/gpt_04.json` | Equipe – produzido na execução | 10653 |
| `amostras/extensao_integrada_checkpoint_publicado/gpt_05.json` | Equipe – produzido na execução | 10394 |
| `amostras/extensao_integrada_checkpoint_publicado/pipeline_00.json` | Equipe – produzido na execução | 1672 |
| `amostras/extensao_integrada_checkpoint_publicado/pipeline_01.json` | Equipe – produzido na execução | 1254 |
| `amostras/extensao_integrada_checkpoint_publicado/pipeline_02.json` | Equipe – produzido na execução | 820 |
| `amostras/extensao_integrada_checkpoint_publicado/pipeline_03.json` | Equipe – produzido na execução | 1276 |
| `amostras/extensao_integrada_checkpoint_publicado/pipeline_04.json` | Equipe – produzido na execução | 1798 |
| `amostras/extensao_integrada_checkpoint_publicado/pipeline_05.json` | Equipe – produzido na execução | 1502 |
| `amostras/extensao_integrada_checkpoint_publicado/validacao.html` | Equipe – produzido na execução | 2904 |
| `amostras/gpt4o_piloto/chamada_00.json` | Equipe – produzido na execução | 11373 |
| `amostras/gpt4o_piloto/chamada_01.json` | Equipe – produzido na execução | 11126 |
| `amostras/gpt4o_piloto/chamada_02.json` | Equipe – produzido na execução | 10919 |
| `amostras/gpt4o_piloto/chamada_03.json` | Equipe – produzido na execução | 11622 |
| `amostras/gpt4o_piloto/chamada_04.json` | Equipe – produzido na execução | 11239 |
| `amostras/gpt4o_piloto/chamada_05.json` | Equipe – produzido na execução | 10622 |
| `amostras/gpt4o_piloto/chamada_06.json` | Equipe – produzido na execução | 11115 |
| `amostras/gpt4o_piloto/chamada_07.json` | Equipe – produzido na execução | 10587 |
| `amostras/gpt4o_piloto/chamada_08.json` | Equipe – produzido na execução | 10573 |
| `amostras/gpt4o_piloto/chamada_09.json` | Equipe – produzido na execução | 11466 |
| `amostras/gpt4o_piloto/chamada_10.json` | Equipe – produzido na execução | 10381 |
| `amostras/gpt4o_piloto/chamada_11.json` | Equipe – produzido na execução | 10690 |
| `amostras/gpt4o_piloto/chamada_12.json` | Equipe – produzido na execução | 11071 |
| `amostras/gpt4o_piloto/chamada_13.json` | Equipe – produzido na execução | 10967 |
| `amostras/gpt4o_piloto/chamada_14.json` | Equipe – produzido na execução | 10175 |
| `amostras/gpt4o_piloto/chamada_15.json` | Equipe – produzido na execução | 11440 |
| `amostras/gpt4o_piloto/chamada_16.json` | Equipe – produzido na execução | 11138 |
| `amostras/gpt4o_piloto/chamada_17.json` | Equipe – produzido na execução | 10743 |
| `amostras/gpt4o_piloto/chamadas.jsonl` | Equipe – produzido na execução | 2171 |
| `amostras/gpt4o_piloto/plano.json` | Equipe – produzido na execução | 590 |
| `amostras/gpt4o_v1_v2_v3/` (329 arquivos; ver manifesto) | Equipe – produzido na execução | 2157549 |
| `amostras/rag_filtro_e_reanalise/prompts_sinteticos.json` | Equipe – produzido na execução | 40698 |

## Modelos e metadados de modelos (`03_insumos/modelos/`)

| Arquivo | Origem | Bytes |
|---|---|---:|
| `modelos/bert_checkpoint_publicado/modelo_download.json` | Equipe – produzido na execução | 1276 |
| `modelos/bert_colab_holdout/config.json` | Equipe – produzido na execução | 1575 |
| `modelos/bert_colab_holdout/special_tokens_map.json` | Equipe – produzido na execução | 125 |
| `modelos/bert_colab_holdout/tokenizer.json` | Equipe – produzido na execução | 678055 |
| `modelos/bert_colab_holdout/tokenizer_config.json` | Equipe – produzido na execução | 1271 |
| `modelos/bert_colab_holdout/vocab.txt` | Equipe – produzido na execução | 209528 |
| `modelos/bert_colab_holdout/modelo_download.json` | Equipe – produzido na execução | 2425 |
| `modelos/bert_colab_execucao2/config.json` | Equipe – produzido na execução | 1575 |
| `modelos/bert_colab_execucao2/modelo_download.json` | Equipe – produzido na execução | 2546 |
| `modelos/bert_colab_execucao2/special_tokens_map.json` | Equipe – produzido na execução | 125 |
| `modelos/bert_colab_execucao2/tokenizer.json` | Equipe – produzido na execução | 678055 |
| `modelos/bert_colab_execucao2/tokenizer_config.json` | Equipe – produzido na execução | 1271 |
| `modelos/bert_colab_execucao2/vocab.txt` | Equipe – produzido na execução | 209528 |
| _pesos da 2ª execução (`model.safetensors`, 435734528 bytes): no Hugging Face `VitorMendonca62/veritaplugin-bert-replicacao-execucao2`, revisão `2252be93`; ver `modelo_download.json`_ | | |
| _pesos do holdout (`model.safetensors`, 435734528 bytes): no Hugging Face `VitorMendonca62/veritaplugin-bert-replicacao-holdout`, revisão `e773157a`; ver `modelo_download.json`_ | | |
| `modelos/bert_treinamento_colab/compatibilidade_modelo_api.json` | Equipe – produzido na execução | 1114 |

## Imagens: gráficos e capturas de tela reais (`03_insumos/imagens/`)

| Arquivo | Origem | Bytes |
|---|---|---:|
| `imagens/api_e_replica/replica_feed_real.png` | Equipe – produzido na execução | 48394 |
| `imagens/baseline_tfidf_svm/baseline_confusao.png` | Equipe – produzido na execução | 95905 |
| `imagens/baseline_tfidf_svm/baseline_folds.png` | Equipe – produzido na execução | 34901 |
| `imagens/bert_treinamento_colab/folds_nova_execucao_vs_autoras.png` | Gerado na revisão a partir dos dados da execução | 52288 |
| `imagens/bert_treinamento_colab/holdout_matriz_confusao_recalculada.png` | Gerado na revisão a partir dos dados da execução | 79343 |
| `imagens/bert_treinamento_colab/resultados_bert/holdout_f1_categorias.png` | Equipe – produzido na execução | 43239 |
| `imagens/bert_treinamento_colab/resultados_bert/holdout_matriz_confusao.png` | Equipe – produzido na execução | 67380 |
| `imagens/bert_treinamento_colab/resultados_bert/kfold_f1_categorias_consolidado.png` | Equipe – produzido na execução | 45768 |
| `imagens/bert_treinamento_colab/resultados_bert/kfold_f1_por_fold.png` | Equipe – produzido na execução | 35623 |
| `imagens/bert_treinamento_colab/resultados_bert/kfold_matriz_confusao_consolidada.png` | Equipe – produzido na execução | 78121 |
| `imagens/comparacao/artigo_vs_replicacao.png` | Gerado na revisão a partir dos dados da execução | 63703 |
| `imagens/extensao_integrada/latencias_integradas.png` | Gerado na revisão a partir dos dados da execução | 74154 |
| `imagens/extensao_integrada_bert_colab/modal_colab_00.png` | Equipe – produzido na execução | 143092 |
| `imagens/extensao_integrada_bert_colab/modal_colab_01.png` | Equipe – produzido na execução | 180121 |
| `imagens/extensao_integrada_bert_colab/modal_colab_02.png` | Equipe – produzido na execução | 179125 |
| `imagens/extensao_integrada_bert_colab/modal_colab_03.png` | Equipe – produzido na execução | 171367 |
| `imagens/extensao_integrada_bert_colab/modal_colab_04.png` | Equipe – produzido na execução | 209238 |
| `imagens/extensao_integrada_bert_colab/modal_colab_05.png` | Equipe – produzido na execução | 170351 |
| `imagens/extensao_integrada_checkpoint_publicado/erro_rede.png` | Equipe – produzido na execução | 140460 |
| `imagens/extensao_integrada_checkpoint_publicado/modal_00.png` | Equipe – produzido na execução | 216147 |
| `imagens/extensao_integrada_checkpoint_publicado/modal_01.png` | Equipe – produzido na execução | 202335 |
| `imagens/extensao_integrada_checkpoint_publicado/modal_02.png` | Equipe – produzido na execução | 169348 |
| `imagens/extensao_integrada_checkpoint_publicado/modal_03.png` | Equipe – produzido na execução | 204327 |
| `imagens/extensao_integrada_checkpoint_publicado/modal_04.png` | Equipe – produzido na execução | 201053 |
| `imagens/extensao_integrada_checkpoint_publicado/modal_05.png` | Equipe – produzido na execução | 222520 |
| `imagens/extensao_integrada_checkpoint_publicado/onboarding.png` | Equipe – produzido na execução | 35815 |
| `imagens/extensao_integrada_checkpoint_publicado/replica_index.png` | Equipe – produzido na execução | 338136 |
| `imagens/extensao_integrada_checkpoint_publicado/replica_marketplace.png` | Equipe – produzido na execução | 151254 |
| `imagens/extensao_integrada_checkpoint_publicado/replica_messages.png` | Equipe – produzido na execução | 177533 |
| `imagens/gpt4o_v1_v2_v3/v2_v3_base_legal_por_categoria.png` | Gerado na revisão a partir dos dados da execução | 62485 |
| `imagens/reanalise_sus_juridico/juridico_avaliacao.png` | Gerado na revisão a partir dos dados da execução | 101714 |
| `imagens/reanalise_sus_juridico/sus_escores.png` | Gerado na revisão a partir dos dados da execução | 42481 |

## Tabelas e métricas estruturadas (CSV/JSON) (`03_insumos/tabelas/`)

| Arquivo | Origem | Bytes |
|---|---|---:|
| `tabelas/_controle/mapa_caminhos.csv` | Escrito na revisão | 156152 |
| `tabelas/_controle/registro_origem.json` | Escrito na revisão | 96255 |
| `tabelas/api_e_replica/api_http.json` | Equipe – produzido na execução | 433 |
| `tabelas/api_e_replica/api_testclient.json` | Equipe – produzido na execução | 1287 |
| `tabelas/baseline_investigacao_divergencia/150.json` | Equipe – produzido na execução | 1919 |
| `tabelas/baseline_investigacao_divergencia/151.json` | Equipe – produzido na execução | 1920 |
| `tabelas/baseline_investigacao_divergencia/152_original.json` | Equipe – produzido na execução | 1928 |
| `tabelas/baseline_investigacao_divergencia/comparacao.csv` | Equipe – produzido na execução | 648 |
| `tabelas/baseline_investigacao_divergencia/folds_bert_texto_original.json` | Equipe – produzido na execução | 1953 |
| `tabelas/baseline_investigacao_divergencia/strip_mesmos_folds.json` | Equipe – produzido na execução | 1914 |
| `tabelas/baseline_investigacao_divergencia/verificacao_controles.json` | Equipe – produzido na execução | 143 |
| `tabelas/baseline_tfidf_svm/baseline_confusao.csv` | Equipe – produzido na execução | 447 |
| `tabelas/baseline_tfidf_svm/baseline_erros.csv` | Gerado na revisão a partir dos dados da execução | 19785 |
| `tabelas/baseline_tfidf_svm/baseline_folds.csv` | Gerado na revisão a partir dos dados da execução | 239 |
| `tabelas/baseline_tfidf_svm/baseline_metricas.json` | Equipe – produzido na execução | 2543 |
| `tabelas/baseline_tfidf_svm/baseline_metricas_por_classe.csv` | Gerado na revisão a partir dos dados da execução | 532 |
| `tabelas/baseline_tfidf_svm/baseline_resumo_erros.csv` | Gerado na revisão a partir dos dados da execução | 120 |
| `tabelas/bert_checkpoint_publicado/bert_inferencia.json` | Equipe – produzido na execução | 5726 |
| `tabelas/bert_checkpoint_publicado/bert_reanalise_autores.json` | Equipe – produzido na execução | 286 |
| `tabelas/bert_treinamento_colab/auditoria_zip.json` | Equipe – produzido na execução | 15462 |
| `tabelas/bert_treinamento_colab/comparacao_bert.csv` | Equipe – produzido na execução | 398 |
| `tabelas/bert_treinamento_colab/comparacao_bert.json` | Equipe – produzido na execução | 4785 |
| `tabelas/bert_treinamento_colab/correcao_matplotlib.json` | Equipe – produzido na execução | 242 |
| `tabelas/bert_treinamento_colab/folds_nova_execucao_vs_autoras.csv` | Gerado na revisão a partir dos dados da execução | 343 |
| `tabelas/bert_treinamento_colab/holdout_erros.csv` | Gerado na revisão a partir dos dados da execução | 1688 |
| `tabelas/bert_treinamento_colab/holdout_matriz_confusao.csv` | Gerado na revisão a partir dos dados da execução | 223 |
| `tabelas/bert_treinamento_colab/holdout_metricas_por_classe.csv` | Gerado na revisão a partir dos dados da execução | 329 |
| `tabelas/bert_treinamento_colab/holdout_reavaliacao_cpu.json` | Equipe – produzido na execução | 1863 |
| `tabelas/bert_treinamento_colab/holdout_teste_estatistico.json` | Gerado na revisão a partir dos dados da execução | 1154 |
| `tabelas/bert_treinamento_colab/resultados_bert/holdout_metricas.json` | Equipe – produzido na execução | 1325 |
| `tabelas/bert_treinamento_colab/resultados_bert/kfold_fold1_metricas.json` | Equipe – produzido na execução | 119 |
| `tabelas/bert_treinamento_colab/resultados_bert/kfold_fold2_metricas.json` | Equipe – produzido na execução | 120 |
| `tabelas/bert_treinamento_colab/resultados_bert/kfold_fold3_metricas.json` | Equipe – produzido na execução | 105 |
| `tabelas/bert_treinamento_colab/resultados_bert/kfold_fold4_metricas.json` | Equipe – produzido na execução | 120 |
| `tabelas/bert_treinamento_colab/resultados_bert/kfold_fold5_metricas.json` | Equipe – produzido na execução | 120 |
| `tabelas/bert_treinamento_colab/resultados_bert/kfold_resultado_final.json` | Equipe – produzido na execução | 1465 |
| `tabelas/comparacao/resumo_metricas.csv` | Gerado na revisão a partir dos dados da execução | 913 |
| `tabelas/dados_auditoria/auditoria_complementar.json` | Equipe – produzido na execução | 1023 |
| `tabelas/dados_auditoria/auditoria_dados.json` | Equipe – produzido na execução | 8088 |
| `tabelas/extensao_integrada/latencias_integradas.csv` | Gerado na revisão a partir dos dados da execução | 2004 |
| `tabelas/extensao_integrada/latencias_resumo.csv` | Gerado na revisão a partir dos dados da execução | 687 |
| `tabelas/extensao_integrada_bert_colab/browser_integracao_colab.json` | Equipe – produzido na execução | 14498 |
| `tabelas/extensao_integrada_bert_colab/integracao_resumo.json` | Equipe – produzido na execução | 2626 |
| `tabelas/extensao_integrada_bert_colab/verificacao_modal_api.json` | Equipe – produzido na execução | 1664 |
| `tabelas/extensao_integrada_checkpoint_publicado/browser_offline.json` | Equipe – produzido na execução | 2447 |
| `tabelas/extensao_integrada_checkpoint_publicado/browser_paid.json` | Equipe – produzido na execução | 12352 |
| `tabelas/extensao_integrada_checkpoint_publicado/busca_local.json` | Equipe – produzido na execução | 23486 |
| `tabelas/extensao_integrada_checkpoint_publicado/controle_gasto_verificado.json` | Equipe – produzido na execução | 204 |
| `tabelas/extensao_integrada_checkpoint_publicado/encerramento.json` | Equipe – produzido na execução | 119 |
| `tabelas/extensao_integrada_checkpoint_publicado/paginas_replica.json` | Equipe – produzido na execução | 500 |
| `tabelas/extensao_integrada_checkpoint_publicado/resultados.csv` | Equipe – produzido na execução | 1592 |
| `tabelas/extensao_integrada_checkpoint_publicado/resumo.json` | Equipe – produzido na execução | 1159 |
| `tabelas/extensao_integrada_checkpoint_publicado/testes_api_sem_gasto.json` | Equipe – produzido na execução | 710 |
| `tabelas/gpt4o_custos/custos_gpt4o_por_lote.csv` | Gerado na revisão a partir dos dados da execução | 803 |
| `tabelas/gpt4o_piloto/resumo.json` | Equipe – produzido na execução | 169 |
| `tabelas/gpt4o_v1_v2_v3/auditoria_campos_referencias.json` | Equipe – produzido na execução | 6812 |
| `tabelas/gpt4o_v1_v2_v3/comparacao_pipelines.csv` | Equipe – produzido na execução | 33254 |
| `tabelas/gpt4o_v1_v2_v3/controle_configurado.json` | Equipe – produzido na execução | 342 |
| `tabelas/gpt4o_v1_v2_v3/gasto_final.json` | Equipe – produzido na execução | 343 |
| `tabelas/gpt4o_v1_v2_v3/metodo_comparacao.json` | Equipe – produzido na execução | 552 |
| `tabelas/gpt4o_v1_v2_v3/progresso.json` | Equipe – produzido na execução | 368 |
| `tabelas/gpt4o_v1_v2_v3/protocolo_originais.json` | Equipe – produzido na execução | 2168 |
| `tabelas/gpt4o_v1_v2_v3/resumo_final.json` | Equipe – produzido na execução | 689 |
| `tabelas/gpt4o_v1_v2_v3/resumo_pipelines.json` | Equipe – produzido na execução | 2795 |
| `tabelas/gpt4o_v1_v2_v3/testes_controle_gasto.json` | Equipe – produzido na execução | 157 |
| `tabelas/gpt4o_v1_v2_v3/v1_reanalise.json` | Equipe – produzido na execução | 925 |
| `tabelas/gpt4o_v1_v2_v3/v2_v3_por_categoria.csv` | Gerado na revisão a partir dos dados da execução | 962 |
| `tabelas/rag_filtro_e_reanalise/rag_consistencia_autores.json` | Equipe – produzido na execução | 12109 |
| `tabelas/rag_filtro_e_reanalise/rag_reanalise_autores.json` | Equipe – produzido na execução | 1759 |
| `tabelas/rag_filtro_e_reanalise/rag_testes_locais.json` | Equipe – produzido na execução | 6374 |
| `tabelas/reanalise_sus_juridico/juridico_contagens.csv` | Gerado na revisão a partir dos dados da execução | 1232 |
| `tabelas/reanalise_sus_juridico/juridico_reanalise.json` | Equipe – produzido na execução | 2379 |
| `tabelas/reanalise_sus_juridico/sus_escores.csv` | Equipe – produzido na execução | 132 |
| `tabelas/reanalise_sus_juridico/sus_reanalise.json` | Equipe – produzido na execução | 1394 |

## Scripts, notebooks, patches e extensão adaptada (`03_insumos/scripts/`)

| Arquivo | Origem | Bytes |
|---|---|---:|
| `scripts/api_e_replica/adaptacao_extensao.patch` | Equipe – produzido na execução | 1937 |
| `scripts/bert_treinamento_colab/adaptacao.patch` | Equipe – produzido na execução | 360 |
| `scripts/bert_treinamento_colab/preparar_modelo.py` | Equipe – produzido na execução | 952 |
| `scripts/bert_treinamento_colab/treinar_bert.py` | Equipe – produzido na execução | 15983 |
| `scripts/bert_treinamento_colab/treinar_bert_original.py` | Equipe – produzido na execução | 15894 |
| `scripts/colab/Corrigir_Matplotlib_Colab.py` | Equipe – documento ou código | 1857 |
| `scripts/colab/Preparar_ambiente_Colab.py` | Equipe – documento ou código | 2035 |
| `scripts/colab/Treinar_BERTimbau_VeritaPlugin_v3.ipynb` | Equipe – documento ou código | 13895 |
| `scripts/extensao_local_adaptada/background.js` | Equipe – documento ou código | 1206 |
| `scripts/extensao_local_adaptada/bootstrap.min.css` | Equipe – documento ou código | 232803 |
| `scripts/extensao_local_adaptada/content.js` | Equipe – documento ou código | 13562 |
| `scripts/extensao_local_adaptada/icon.png` | Equipe – documento ou código | 65367 |
| `scripts/extensao_local_adaptada/manifest.json` | Equipe – documento ou código | 853 |
| `scripts/extensao_local_adaptada/setup.html` | Equipe – documento ou código | 15319 |
| `scripts/extensao_local_adaptada/setup.js` | Equipe – documento ou código | 5213 |

## Ambiente, versões e proveniência (`03_insumos/ambiente/`)

| Arquivo | Origem | Bytes |
|---|---|---:|
| `ambiente/ambiente_e_proveniencia/ambiente.txt` | Equipe – produzido na execução | 4341 |
| `ambiente/ambiente_e_proveniencia/integridade_repositorios.json` | Equipe – produzido na execução | 427 |
| `ambiente/ambiente_e_proveniencia/pacote_requirements-lock.txt` | Equipe – documento ou código | 1142 |
| `ambiente/ambiente_e_proveniencia/pacote_requirements-validacao.txt` | Equipe – documento ou código | 1190 |
| `ambiente/ambiente_e_proveniencia/proveniencia.json` | Equipe – produzido na execução | 1440 |
| `ambiente/ambiente_e_proveniencia/verificacao_final.json` | Equipe – produzido na execução | 695 |
| `ambiente/ambiente_e_proveniencia/versoes.json` | Equipe – produzido na execução | 1762 |
| `ambiente/baseline_investigacao_divergencia/proveniencia.json` | Equipe – produzido na execução | 1456 |
| `ambiente/bert_treinamento_colab/bootstrap_versoes.txt` | Equipe – produzido na execução | 112 |
| `ambiente/bert_treinamento_colab/commit.txt` | Equipe – produzido na execução | 40 |
| `ambiente/bert_treinamento_colab/entradas_sha256.json` | Equipe – produzido na execução | 3213 |
| `ambiente/bert_treinamento_colab/gpu.txt` | Equipe – produzido na execução | 1689 |
| `ambiente/bert_treinamento_colab/modelo_base.json` | Equipe – produzido na execução | 258 |
| `ambiente/bert_treinamento_colab/requirements-lock.txt` | Equipe – produzido na execução | 1340 |
| `ambiente/extensao_integrada_bert_colab/navegador_final.json` | Equipe – produzido na execução | 140 |
| `ambiente/extensao_integrada_checkpoint_publicado/integridade_codigo.json` | Equipe – produzido na execução | 632 |
| `ambiente/extensao_integrada_checkpoint_publicado/navegador.json` | Equipe – produzido na execução | 260 |
| `ambiente/gpt4o_v1_v2_v3/verificacao_entrega.json` | Equipe – produzido na execução | 588 |

## Retreino com o dataset unificado (16–17/11/2026)

| `modelos/retreino_dataset_unificado/modelo_download.json` | Equipe – produzido na execução | 2371 |
| `scripts/baixar_modelo_hf.py` | Equipe – documento ou código | 1627 |

| Arquivo | Origem | Bytes |
|---|---|---:|
| `02_relatorios/retreino_dataset_unificado.md` | Equipe – documento ou código | 24617 |
| `logs/retreino_dataset_unificado/treinamento.log` | Equipe – produzido na execução | 484710 |
| `logs/retreino_dataset_unificado/status.json` | Equipe – produzido na execução | 891 |
| `logs/retreino_dataset_unificado/baseline_inferencia_plugin.log` | Equipe – produzido na execução | 30 |
| `logs/retreino_dataset_unificado/baseline_inferencia_replicacao1.log` | Equipe – produzido na execução | 91 |
| `logs/retreino_dataset_unificado/baseline_inferencia_replicacao2.log` | Equipe – produzido na execução | 91 |
| `ambiente/retreino_dataset_unificado/bootstrap_versoes.txt` | Equipe – produzido na execução | 111 |
| `ambiente/retreino_dataset_unificado/gpu.txt` | Equipe – produzido na execução | 1689 |
| `ambiente/retreino_dataset_unificado/modelo_base.json` | Equipe – produzido na execução | 258 |
| `ambiente/retreino_dataset_unificado/requirements-lock.txt` | Equipe – produzido na execução | 1320 |
| `ambiente/retreino_dataset_unificado/meta_execucao.json` | Equipe – produzido na execução | 934 |
| `scripts/retreino_dataset_unificado/analisar_dataset.py` | Equipe – documento ou código | 7551 |
| `scripts/retreino_dataset_unificado/preparar_splits.py` | Equipe – documento ou código | 6036 |
| `scripts/retreino_dataset_unificado/treinar_retreino.py` | Equipe – documento ou código | 8621 |
| `scripts/retreino_dataset_unificado/comparar.py` | Equipe – documento ou código | 11994 |
| `scripts/retreino_dataset_unificado/prever.py` | Equipe – documento ou código | 1687 |
| `scripts/retreino_dataset_unificado/resumo_baseline.py` | Equipe – documento ou código | 3095 |
| `scripts/retreino_dataset_unificado/criar_notebook.py` | Equipe – documento ou código | 13261 |
| `tabelas/retreino_dataset_unificado/analise_dataset.json` | Equipe – produzido na execução | 4285 |
| `tabelas/retreino_dataset_unificado/matriz_fonte_x_classe.csv` | Equipe – produzido na execução | 333 |
| `tabelas/retreino_dataset_unificado/exemplos_quase_duplicatas.json` | Equipe – produzido na execução | 1322 |
| `tabelas/retreino_dataset_unificado/resumo_splits.json` | Equipe – produzido na execução | 3601 |
| `tabelas/retreino_dataset_unificado/baseline_resumo.json` | Equipe – produzido na execução | 12778 |
| `tabelas/retreino_dataset_unificado/comparacao.md` | Equipe – produzido na execução | 8944 |
| `tabelas/retreino_dataset_unificado/comparacao.json` | Equipe – produzido na execução | 7603 |
| `amostras/retreino_dataset_unificado/entrada/BrScamsFacebook_Unificado_2.xlsx` | Equipe – documento ou código | 121186 |
| `amostras/retreino_dataset_unificado/dados/pool_dedup.csv` | Equipe – produzido na execução | 276213 |
| `amostras/retreino_dataset_unificado/dados/dedup_removidos.csv` | Equipe – produzido na execução | 2439 |
| `amostras/retreino_dataset_unificado/dados/splits.json` | Equipe – produzido na execução | 97100 |
| `amostras/retreino_dataset_unificado/baseline/pred_plugin_publicado.csv` | Equipe – produzido na execução | 76206 |
| `amostras/retreino_dataset_unificado/baseline/pred_1a_execucao.csv` | Equipe – produzido na execução | 75996 |
| `amostras/retreino_dataset_unificado/baseline/pred_2a_execucao.csv` | Equipe – produzido na execução | 76230 |
| `scripts/colab/Retreino_BERTimbau_Unificado_Colab_v3.ipynb` | Equipe – documento ou código | 15603 |
| `modelos/retreino_dataset_unificado/modelo_candidato_metadados.json` | Equipe – produzido na execução | 3357 |
| `modelos/retreino_dataset_unificado/modelo_download.json` | Equipe – produzido na execução | 2365 |
| `amostras/retreino_dataset_unificado/experimentos/` (83 arquivos de 33 experimentos; ver manifesto) | Equipe – produzido na execução | 186050 |
