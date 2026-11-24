# Validação do treinamento BERT recebido do Colab

**Os seis treinamentos foram concluídos e seus artefatos passaram pelas verificações disponíveis.** A validação cruzada ficou numericamente próxima do artigo; o resultado holdout não foi reproduzido.

| Métrica | Artigo | Nova execução |
|---|---:|---:|
| F1-macro médio, cinco folds | 0,763 ± 0,034 | **0.765588 ± 0.036405** |
| F1-macro holdout | 0,828 | **0.688197** |
| Acurácia holdout | 82,2% | **68.89%** |
| Acurácia CV consolidada | 76,0% | **76.44%** |

O F1 médio CV ficou +0.2588 pontos percentuais em relação ao artigo arredondado. A diferença é +0.2288 pp em relação aos JSONs exatos das autoras. Proximidade numérica e sobreposição de desvios padrão não comprovam equivalência estatística nem reprodução de 100% do artigo.

No holdout, o F1 ficou -13.9803 pp em relação ao artigo. A reavaliação local do modelo salvo encontrou **31/45 acertos**, confirmando o resultado de GPU. O artefato das autoras tem 37/45 acertos; são seis acertos a menos nesta execução, sem dados suficientes para identificar os casos divergentes das autoras.

## Execução e integridade

- Commit do treinamento: 0487415058c0cc087dfba4f151652cca82e7d3e2.
- O script original recebido é idêntico ao arquivo auditado das autoras; o executado difere somente no caminho do modelo base fixado.
- Os 29 arquivos de divisão são byte a byte idênticos aos versionados. O manifesto de entradas foi conferido.
- Base: neuralmind/bert-base-portuguese-cased, revisão 94d69c95f98f7d5b2a8700c420230ae10def0baa.
- GPU registrada: Tesla T4, 15.360 MiB. PyTorch 2.4.0+cu121; Transformers 4.44.2; datasets 2.21.0; accelerate 0.34.2; scikit-learn 1.5.2; NumPy 1.26.4; matplotlib 3.9.2.
- Python de treinamento 3.12.14; kernel Colab 3.13.15; bootstrap uv 0.12.21, conforme arquivo recebido. Essas são as versões observadas, sem inferir identidade completa com o ambiente histórico das autoras.
- Status final complete, código de saída zero, duração 1206.04 segundos (**20 min 6 s**), excluindo preparação/instalação.
- O log contém seis resumos de treinamento, todos terminando na época 4, além do holdout e dos cinco relatórios de fold. A tentativa anterior de Matplotlib falhou em cerca de dois segundos e está preservada separadamente; não foi confundida com treinamento concluído.

## Resultados por fold

| Fold | F1-macro novo |
|---|---:|
| 1 | 0.787339 |
| 2 | 0.810974 |
| 3 | 0.704032 |
| 4 | 0.774816 |
| 5 | 0.750781 |

**Comparação fold a fold (adicionada na revisão):** os folds 1, 3, 4 e 5 são idênticos aos JSONs das autoras até a 16ª casa decimal; somente o fold 2 difere (0,810974 contra 0,799536, +1,14 pp). Ver `03_insumos/tabelas/bert_treinamento_colab/folds_nova_execucao_vs_autoras.csv`.

A média por fold (0,765588) difere do F1-macro das 450 predições consolidadas (0,764904). O desvio usa ddof=0. Não são intervalos de confiança.

## Reavaliação local e integração

Carregamos somente os pesos safetensors e os arquivos do tokenizador; training_args.bin não foi desserializado nem extraído. Recalculamos os 45 exemplos do teste holdout em CPU, dois threads, com padding fixo de 512 tokens. Para limitar memória, o batch de avaliação local foi 2, enquanto o treinamento usa 16. O F1, a acurácia e todos os F1 por classe coincidiram com o relatório da GPU.

O modelo foi ligado a uma cópia separada do classificador/API, sem substituir o checkpoint publicado usado nos testes anteriores. O mapeamento das seis classes é compatível. O classificador original executou exemplos de funcionamento; os endpoints locais health e os erros de entrada/credencial funcionaram. Na auditoria inicial não houve chamada GPT. Posteriormente, seis análises completas com extensão e GPT foram concluídas com este checkpoint; ver [integracao_BERT_Colab_GPT4o.md](integracao_BERT_Colab_GPT4o.md). As seis análises integradas anteriores continuam atribuídas ao modelo publicado pelas autoras.

## Interpretação e limitações

**Teste estatístico do holdout (adicionado na revisão):** 31/45 contra 37/45 acertos. Fisher exato bicaudal p ≈ 0,22; IC95% Clopper-Pearson 53,4%–81,8% (nova execução) e 67,9%–92,0% (autoras). Com n=45, não há evidência estatística de diferença, o que também não prova equivalência. Como as autoras não publicaram predições por exemplo, um teste pareado (McNemar) não é possível. Ver `holdout_teste_estatistico.json`.

A diferença de holdout não é falha de leitura dos pesos: as métricas foram recalculadas localmente e confirmadas. Não há causa demonstrada para a divergência histórica. Uma fonte possível de variação é que o código original constrói a cabeça de classificação antes de o Trainer aplicar a seed; preservamos essa ordem. A revisão base e o ambiente exatos das autoras não estão completamente estabelecidos. Essas são hipóteses/limitações, não causas comprovadas.

No k-fold, o teste também escolhe a época; duplicatas cruzadas e folds distintos entre baseline e BERT foram preservados. A vantagem descritiva sobre nosso baseline original é de aproximadamente 6,22 pp de F1-macro médio, mas essa comparação usa folds diferentes e não demonstra ganho pareado atribuível apenas ao modelo. Não refizemos treinamento para aproximar os valores publicados.

O código original salva apenas o modelo holdout e exclui checkpoints dos folds; por isso, os cinco folds puderam ser auditados por código, dados, logs e métricas, mas não reavaliados a partir de cinco modelos ou predições brutas preservadas. A amostra holdout tem 45 textos; seus resultados precisam ser apresentados separadamente da CV.

## Arquivos

- `evidencias/execucao/treinamento_colab/`: log, versões, status, scripts recebidos, splits, métricas, gráficos e auditorias.
- `holdout_reavaliacao_cpu.json` e `holdout_predicoes_cpu.json`: recálculo local das métricas, usando o próprio teste reservado do treinamento recebido.
- `compatibilidade_modelo_api.json`: teste local sem GPT.
- `treinamento_BERT_Colab_original.zip`: arquivo original completo, incluindo modelo, preservado separadamente do pacote leve de evidências.

V2/V3 foram posteriormente reexecutadas em 80 exemplos cada; V1 foi somente reanalisada, sem GPT-5. As divergências de baseline/holdout e lacunas históricas permanecem. Este recebimento completa a execução do treinamento prevista, sem transformar resultados próximos em reprodução exata.
