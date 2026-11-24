# Validação integrada do VeritaPlugin

Seis análises reais concluíram o fluxo Chromium → extensão MV3 → API FastAPI → BERT publicado → GPT-4o → filtro original → modal. As seis categorias preditas foram cobertas, incluindo Seguro. No momento deste lote, o novo modelo do Colab ainda não havia sido recebido. Posteriormente, foi auditado conforme validacao_treinamento_BERT.md; este lote continua atribuído ao checkpoint publicado.

## Ambiente e adaptações

Playwright 1.64.0, Chromium instalado em pasta isolada, perfil temporário persistente, execução headless e serviços vinculados a 127.0.0.1 nas portas 5500 e 8080. A extensão recebeu apenas as adaptações locais já registradas no patch; a página `validacao.html` foi adicionada ao lado da réplica original para controlar os textos. Não foi usada conta real do Facebook.

O checkpoint foi `brunanoroes/veritaplugin-bert`, revisão d05bc15ad4821dbf629ca9473fc30387299b44de, CPU com dois threads. Foram necessárias 34 inferências locais para selecionar o primeiro exemplo de cada categoria predita, buscando no corpus por alternância de rótulos. Esses exemplos podem fazer parte do treinamento original: não constituem avaliação independente de acurácia. A seleção proposital também impede estimar uma distribuição natural de erros.

A API original e seus contratos foram preservados. Um wrapper instrumentou classificação e geração, restringiu o lote a seis textos exatos e uma tentativa por texto, limitou saída a 1.200 tokens e desativou retries. O timeout de 60 segundos e o controle de gasto são diferenças explícitas em relação ao original. A chave real permaneceu no backend via .env; o formulário de onboarding foi testado com uma chave fictícia e depois o valor do navegador foi esvaziado. Portanto, não se validou autenticação de uma chave real armazenada pela extensão.

## Casos medidos

| Caso | Categoria predita | Confiança softmax | BERT (s) | GPT (s) | Clique até modal (s) |
|---|---|---:|---:|---:|---:|
| 1 | Golpes Baseados Em Relacionamento | 0.4760 | 0.459 | 4.116 | 4.675 |
| 2 | Ataques de Phishing e Roubo de Dados | 0.5374 | 0.483 | 2.704 | 3.273 |
| 3 | Seguro | 0.2030 | 0.308 | 1.868 | 2.316 |
| 4 | Golpes de Desinformação Digital | 0.4233 | 0.470 | 2.677 | 3.263 |
| 5 | Golpes de Ganho Financeiro Ilusório | 0.3021 | 0.947 | 2.408 | 3.444 |
| 6 | Fraudes em Lojas Virtuais Falsas | 0.2244 | 0.338 | 3.646 | 4.069 |

O caso 1 é a primeira requisição paga da sessão do navegador, mas o processo BERT já havia sido carregado e exercitado nos testes sem gasto. Estes tempos não incluem inicialização do modelo, API ou navegador. O tempo total começa imediatamente antes do comando de clique do Playwright e termina ao detectar o modal no DOM, incluindo a automação. Não mede quando um usuário humano percebe o modal. Nenhuma garantia de 2–4 segundos pode ser inferida de seis exemplos.

As capturas modal_00.png a modal_05.png mostram as saídas reais. Modal, remoção do carregamento e fechamento foram verificados nos seis casos. O cabeçalho Seguro foi exercitado. O campo `risco` da API representa confiança softmax convertida em inteiro, não probabilidade calibrada de fraude; o modal original não o exibe.

## Testes sem chamadas externas

- Onboarding detectou o health local e salvou configuração com chave fictícia.
- Botão, destaque, cancelamento por Esc e cancelamento por botão funcionaram.
- API retornou 400 para texto vazio, 422 para entrada sem mensagem, 401 sem credencial e 502 quando a geração foi bloqueada pelo controle de gasto.
- Navegador em modo offline exibiu `Failed to fetch` e retirou o carregamento. Trata-se de falha de rede induzida; não foi necessário derrubar o servidor.
- O controle de gasto impediu uma chamada acima do teto antes de construir o cliente OpenAI. Os testes iniciais não criaram reservas pagas.
- Após o lote, uma tentativa repetida recebeu erro e não criou uma sétima reserva.

## Limitações e achados

O conteúdo enviado é `e.target.innerText`. Ao selecionar a região de um parágrafo que contém spans, o elemento efetivamente clicado pode ser apenas o span: no diagnóstico foi enviado “Trecho inicial.” em vez de “Trecho inicial. Trecho final.”. A limitação foi registrada sem corrigir o código.

A ausência de erros de API e a pertinência das citações à lista permitida não comprovam a validade jurídica das recomendações. Os rótulos do corpus e do BERT constam lado a lado no CSV; não foi calculada acurácia do checkpoint nesses exemplos potencialmente usados em treinamento.

O caso da reunião de condomínio foi examinado nas evidências do piloto anterior, sem nova chamada: o GPT reconheceu ausência de evidência explícita de golpe, mas recomendou bloquear/denunciar. Isso é uma inconsistência observada na replicação, não uma afirmação de que o artigo documentava esse erro.

## Consumo e encerramento

Novas chamadas: 6; custo calculado sem desconto de cache: **US$ 0.036033**. Somado ao piloto: **US$ 0.153005**, dentro do teto total de US$ 1. O saldo estimado é US$ 0.846995. Esses números usam os tokens retornados e os preços documentados, não uma consulta ao faturamento da conta. O modelo retornado nas seis respostas foi gpt-4o-2024-08-06.

O controle de gasto foi bloqueado novamente após o lote; novas chamadas exigem nova liberação de orçamento. O perfil temporário será removido e os serviços de teste encerrados.

Evidências em `evidencias/execucao/validacao_integrada/`: casos e busca, testes HTTP, resultados CSV, chamadas brutas, pipeline filtrado, navegador e capturas. A instrumentação está em `evidencias/scripts/api_validacao.py` e o roteiro em `validar_extensao.py`.


## Páginas originais da réplica

Também foram abertas index.html, marketplace.html e messages.html com a extensão instalada. As três responderam 200, receberam o botão e permitiram entrar/sair da seleção por Esc. As capturas replica_index.png, replica_marketplace.png e replica_messages.png e o registro paginas_replica.json documentam essa cobertura. Não foram feitas chamadas GPT adicionais nessas páginas.


## Etapa posterior com outro checkpoint

Este relatório preserva a validação inicial com o modelo publicado. Seis novas análises com nosso BERT Colab foram concluídas separadamente, conforme [integracao_BERT_Colab_GPT4o.md](integracao_BERT_Colab_GPT4o.md). Os tempos e custos das duas etapas não foram misturados.
