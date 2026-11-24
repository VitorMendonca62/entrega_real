# Investigação do baseline TF-IDF + SVM

A execução original é repetível no ambiente documentado, mas não confirma os valores do artigo (aproximadamente 0,67) nem do README (0,711 ± 0,027). Os diagnósticos planejados não explicaram a divergência.

| Procedimento | scikit-learn | F1-macro médio | DP populacional |
|---|---:|---:|---:|
| 152_original | 1.5.2 | 0.703389 | 0.027903 |
| 150 | 1.5.0 | 0.703389 | 0.027903 |
| 151 | 1.5.1 | 0.703389 | 0.027903 |
| strip_mesmos_folds | 1.5.2 | 0.703389 | 0.027903 |
| folds_bert_texto_original | 1.5.2 | 0.702840 | 0.037777 |

## Controle do experimento

O script original foi executado sem alterações. Todas as versões usaram o mesmo Python e as mesmas versões de NumPy, pandas, SciPy, joblib, threadpoolctl e openpyxl, registradas em cada JSON. As versões alternativas do scikit-learn foram instaladas sem dependências em pastas separadas. Não houve busca de hiperparâmetros.

O F1 0,703389 ± 0,027903 foi reproduzido exatamente nas três versões 1.5.0, 1.5.1 e 1.5.2. Comparações das predições e dependências constam no resumo estruturado. O valor de 0,67 é aproximado no artigo; a diferença em pontos percentuais não equivale a um teste estatístico.

## Dados e histórico

As duas planilhas têm 450 registros e conteúdo/ordem de linhas idênticos: True. Hashes binários idênticos: True. Há 9 mensagens com espaços nas extremidades e 2 duplicatas exatas de mensagem. Valores ausentes: {'Mensagem': 0, 'Categoria': 0, 'Dataset': 0}.

O histórico Git completo tem três commits: criação inicial, inclusão conjunta do script e dataset em 24/05/2026, e inclusão de README/licença em 19/07/2026. O script não teve uma revisão histórica alternativa disponível. O histórico completo foi recuperado sem mudar o commit do checkout.

## Variantes diagnósticas

Remover espaços nas extremidades, mantendo os mesmos folds, não alterou o F1 nem as predições. O TF-IDF padrão já ignora esses espaços na tokenização.

Usar as partições versionadas do BERT, com os textos originais do baseline, produziu 0,702840 ± 0,037777. Isso demonstra que a partição muda o resultado, mas essa variante tampouco reproduziu o artigo ou o README. A correspondência de linhas duplicadas foi feita por texto normalizado, rótulo e origem, consumindo ocorrências; duplicatas idênticas são indistinguíveis por esse identificador, sem alteração do texto efetivamente fornecido ao modelo.

## Conclusão

Nas condições testadas, versões 1.5.x do scikit-learn e espaços nas extremidades não explicam a divergência. A troca de folds também não recupera os valores declarados. A causa permanece não estabelecida. Seriam necessários os logs, ambiente e entradas exatos que produziram o número publicado para determinar sua origem. Não há evidência para atribuir erro às autoras ou declarar equivalência estatística.

Evidências: `evidencias/execucao/investigacao_baseline/` contém logs, versões, avisos, métricas por fold, predições, proveniência e comparação CSV. Não foram usadas chamadas OpenAI nesta investigação.
