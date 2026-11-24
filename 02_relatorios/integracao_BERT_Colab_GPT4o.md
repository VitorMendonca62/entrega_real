# Integração final com o BERT treinado no Colab

Seis casos passaram pelo fluxo Chromium → extensão MV3 → API local → modelo holdout Colab → contexto → GPT-4o → filtro → modal. As seis categorias preditas foram cobertas, incluindo Seguro. O checkpoint publicado das autoras foi preservado e os resultados anteriores continuam separados.

## Procedimento

Selecionamos o primeiro exemplo de cada categoria predita entre os 45 testes holdout, confirmando a previsão com a função original do classificador. A seleção de exemplos por categoria não é uma nova estimativa de acurácia; o teste completo de 45 já foi avaliado no relatório BERT. Não mudamos rótulos ou forçamos classes.

A interface pública manteve os campos categoria, risco, explicacao, baseLegal e acaoRecomendada. Os seis POSTs responderam 200. Texto extraído, categoria, remoção do carregamento, modal e botão Fechar foram conferidos. O valor risco continua representando confiança softmax, não probabilidade calibrada de fraude. A chave real ficou no backend; o campo de chave do navegador ficou vazio.

A execução foi headless em Chromium com extensão real e perfil temporário persistente, com página controlada local. Os arquivos originais de API/classificador/prompt/filtro foram preservados; somente configuração e instrumentação externas foram usadas. Nenhuma correção do extrator ou filtro foi incorporada.

## Resultados

| Caso | Categoria predita | BERT (s) | GPT (s) | Clique até modal (s) |
|---|---|---:|---:|---:|
| 1 | Seguro | 0.970 | 3.463 | 4.526 |
| 2 | Ataques de Phishing e Roubo de Dados | 0.236 | 3.419 | 3.724 |
| 3 | Golpes de Desinformação Digital | 0.219 | 2.401 | 2.686 |
| 4 | Golpes de Ganho Financeiro Ilusório | 0.201 | 2.656 | 2.935 |
| 5 | Golpes Baseados Em Relacionamento | 0.190 | 3.465 | 3.703 |
| 6 | Fraudes em Lojas Virtuais Falsas | 0.223 | 2.522 | 2.826 |

O cronômetro inclui o comando de clique do Playwright e termina ao detectar o modal no DOM. O modelo já estava carregado; isso não mede partida a frio nem percepção humana. Uma execução por categoria não estabelece garantia de latência. Capturas reais estão em modal_colab_00.png a modal_colab_05.png.

Diferentemente do piloto anterior, estas chamadas não tiveram limite explícito de saída, preservando a chamada original. Retries foram desativados, timeout de 90 s e reserva máxima de custo foram adicionados. Não houve chamada GPT-5. O perfil temporário foi removido, os serviços locais encerrados e o gate fechado após os experimentos.

Custo das seis chamadas: US$ 0.033985, calculado pelos tokens sem desconto de cache. O hash do modelo está em casos_integracao.json e coincide com o manifesto do modelo recebido do Colab.

## Concordância com o corpus e limites das recomendações

O fluxo técnico completou 6/6, mas a categoria coincidiu com o rótulo publicado em 4/6 dos casos selecionados. O caso apresentado como Seguro tinha rótulo Relacionamento; outro caso de Loja foi classificado como Phishing. São erros frente aos rótulos do corpus, preservados no fluxo. A seleção por previsão não estima acurácia. O teste completo continua 31/45.

| Caso | Rótulo do corpus | Categoria predita | Confiança softmax |
|---|---|---|---:|
| 1 | Golpes Baseados Em Relacionamento | Seguro | 0.2883 |
| 2 | Fraudes em Lojas Virtuais Falsas | Ataques de Phishing e Roubo de Dados | 0.3274 |
| 3 | Golpes de Desinformação Digital | Golpes de Desinformação Digital | 0.4082 |
| 4 | Golpes de Ganho Financeiro Ilusório | Golpes de Ganho Financeiro Ilusório | 0.6493 |
| 5 | Golpes Baseados Em Relacionamento | Golpes Baseados Em Relacionamento | 0.4822 |
| 6 | Fraudes em Lojas Virtuais Falsas | Fraudes em Lojas Virtuais Falsas | 0.3122 |

As explicações seguem a categoria do classificador e podem propagar seu erro. Campos exibidos e referências permitidas foram conferidos; não houve nova avaliação especializada da pertinência jurídica ou da eficácia das recomendações. O primeiro caso foi a primeira requisição paga desta replicação, com o modelo já carregado.
