# Guia para apresentar o projeto VeritaPlugin

Este guia explica, em linguagem simples, o que o projeto faz, como foi feita a replicação e o quanto os resultados coincidiram com os do artigo. Foi preparado a partir do conteúdo de `entrega_real`: artigo e materiais das autoras, relatórios, evidências, tabelas e integração da equipe. Os resultados publicados pelas autoras e os resultados obtidos pela equipe são identificados separadamente.

## Resumo em poucas frases

O VeritaPlugin é uma extensão de navegador pensada para ajudar a reconhecer possíveis fraudes em textos do Facebook. O sistema combina um classificador de texto chamado BERTimbau com o GPT-4o: o primeiro escolhe uma categoria, e o segundo produz uma explicação e uma recomendação, usando informações legais associadas à categoria. A equipe reproduziu várias partes do estudo e fez o fluxo funcionar localmente, mas **não reproduziu todos os resultados**. A validação cruzada do BERT ficou muito próxima à publicada; o teste holdout e o baseline divergiram. Portanto, a conclusão correta é **replicação parcial**, não reprodução integral nem validação de que o produto detecta golpes com segurança no uso real.

## O que o sistema tenta fazer

O projeto recebe o texto selecionado no navegador e percorre esta sequência:

1. A extensão captura o texto selecionado.
2. Uma API local recebe o texto e o encaminha ao classificador.
3. O BERTimbau atribui uma das seis classes: cinco categorias de fraude e **Seguro**.
4. O sistema usa a categoria para obter um conjunto de informações legais previamente associado a ela.
5. O GPT-4o recebe o texto, a categoria e o contexto; deve retornar campos estruturados com motivo, base legal e ação recomendada.
6. Um filtro verifica as referências legais retornadas contra a lista permitida para aquela categoria.
7. A extensão mostra a resposta em uma janela (modal) no navegador.

O artigo descreve a extensão, a API, o classificador e a geração de explicações. O escopo é texto: não analisa imagens ou áudio. A recuperação de contexto legal descrita é baseada em um dicionário por categoria, não em uma busca inteligente por documentos. A explicação depende da categoria predita: se o classificador errar, a etapa seguinte pode construir uma explicação sobre uma premissa errada.

## Passo a passo do trabalho da equipe

### 1. Entender e organizar as fontes

A equipe leu o artigo e reuniu os repositórios, planilhas, modelos, scripts, capturas e documentos disponibilizados pelas autoras. O material original foi separado dos arquivos produzidos pela equipe. Isso é importante para distinguir uma métrica publicada de uma métrica calculada agora e para permitir que outra pessoa confira de onde veio cada número.

O artigo estudado é *VeritaPlugin: Uma Extensão de Navegador para Detecção Semântica de Fraudes no Facebook*, de Norões, Rocha e Motta, publicado no SBSeg 2026. A entrega registra os commits e revisões de modelos consultados. Essa conferência de origem ajuda na rastreabilidade, mas não prova que cada checkpoint corresponde exatamente à rodada histórica que gerou todos os resultados do artigo.

### 2. Conferir os dados

O corpus publicado contém 450 textos: 75 em cada uma das seis classes. Os textos vêm de diferentes origens; houve curadoria e, em parte, tradução automática revisada manualmente. A equipe encontrou 448 textos distintos, pois há dois pares de mensagens exatamente duplicadas. Também identificou limitações nas divisões: em alguns folds há mensagens duplicadas entre treino e teste; no treinamento BERT, o conjunto de teste também participa da escolha da época (early stopping), o que pode tornar a avaliação otimista.

A equipe regenerou as divisões do BERT e confirmou que os 29 arquivos de divisão coincidiam byte a byte com os versionados pelas autoras. Essa coincidência fortalece a reprodução da preparação dos dados. Ela não elimina os problemas de duplicatas nem transforma o conjunto em uma avaliação independente.

### 3. Reexecutar o baseline tradicional

Antes do BERT, o repositório das autoras usa um baseline de aprendizado de máquina tradicional:

- **TF-IDF** transforma palavras e combinações de palavras em números. Dá mais destaque a termos úteis para diferenciar textos e menos a termos muito comuns.
- **SVM linear** (implementada como LinearSVC) aprende uma fronteira matemática para separar as categorias a partir desses números.
- A avaliação usa **validação cruzada em cinco partes**: em cada rodada, quatro partes servem para ajustar o modelo e uma para avaliá-lo.

A equipe executou o script original sem alterar o método. O F1-macro médio foi **0,703 ± 0,028**. O artigo reporta aproximadamente **0,67**, e o README atual das autoras informa **0,711 ± 0,027**. A equipe repetiu a execução com scikit-learn 1.5.0, 1.5.1 e 1.5.2: o resultado permaneceu igual. Também verificou espaços no começo/fim dos textos e outras divisões; isso não explicou a diferença. A causa da divergência ficou desconhecida.

### 4. Reexecutar o treinamento do BERTimbau

BERT é uma família de modelos de linguagem que aprende padrões e contexto das palavras em frases. **BERTimbau** é uma versão adaptada ao português brasileiro. Em vez de olhar somente palavras isoladas, o modelo considera o contexto; por isso pode distinguir usos diferentes de uma mesma palavra. As autoras ajustaram o modelo para classificar as seis categorias do corpus.

A equipe recebeu e executou o treinamento em Google Colab, usando uma GPU Tesla T4, com o script e as divisões das autoras. O treinamento usa, entre outros parâmetros, taxa de aprendizado 2e-5, lotes de 16 exemplos, até quatro épocas, limite de 512 tokens e parada antecipada quando a validação deixa de melhorar. **Época** significa uma passagem completa pelos exemplos de treinamento. O modelo foi treinado e avaliado em cinco folds, além de um teste holdout separado.

Resultados da validação cruzada:

| Medida | Artigo | Equipe |
|---|---:|---:|
| F1-macro médio em cinco folds | 0,763 ± 0,034 | 0,766 ± 0,036 |
| Acurácia consolidada | cerca de 76,0% | 76,44% |

Quatro folds coincidiram com os resultados JSON das autoras até muitas casas decimais; o segundo fold da equipe foi 0,811, contra 0,800 das autoras. Isso é uma reprodução muito próxima dessa parte, mas não prova que todas as execuções sejam idênticas.

No **holdout** (um grupo de teste separado do treinamento), o resultado foi diferente:

| Medida | Artigo | Equipe |
|---|---:|---:|
| F1 | 0,828 | 0,688 |
| Acertos | 37 de 45 | 31 de 45 |
| Acurácia | 82,2% | 68,9% |

A diferença é de seis acertos em apenas 45 textos. O teste estatístico disponível não encontrou diferença significativa (Fisher exato, p ≈ 0,22). Isso quer dizer que a amostra é pequena para concluir que os modelos são realmente diferentes; **não** quer dizer que o desempenho seja igual. Como as autoras não publicaram previsões por exemplo, não foi possível fazer a comparação pareada ideal. Não se encontrou a causa da divergência, e não há base para atribuir culpa ou erro a qualquer equipe.

### 5. Testar o classificador e a extensão

A equipe carregou tanto o checkpoint público das autoras quanto o checkpoint treinado no Colab em uma cópia local da API. Instalou a extensão em um Chromium de teste e percorreu o fluxo até a janela final. Foram feitas seis análises integradas com cada checkpoint, cobrindo as seis categorias preditas. Com o BERT Colab, o fluxo técnico terminou em 6/6 casos, mas a categoria coincidiu com o rótulo do corpus em 4/6. Esses seis exemplos foram escolhidos para cobrir categorias; não são uma amostra aleatória e não servem para calcular acurácia.

O tempo medido entre clicar e aparecer a janela variou de 2,3 a 4,7 segundos nos seis casos com o checkpoint publicado e de 2,7 a 4,5 segundos nos seis casos com o checkpoint do Colab. O modelo já estava carregado, e a chamada ao GPT-4o representou a maior parte do tempo. São medições pequenas, feitas em ambiente local de teste; não são garantia de velocidade em qualquer computador ou em produção.

A extensão passou por testes em páginas locais e na réplica das páginas do Facebook, sem usar uma conta real. A equipe testou também situações como texto vazio, falta de credencial e falha de rede. Isso demonstra integração funcional nas condições testadas; não demonstra segurança, acurácia ou eficácia em uso real.

### 6. Avaliar as respostas do GPT-4o e as versões dos prompts

Um **prompt** é a instrução e o contexto enviados ao modelo de linguagem. As versões V1, V2 e V3 mudaram instruções, base legal e/ou filtro, portanto não é possível atribuir qualquer diferença somente à redação do prompt.

A equipe fez um piloto com 18 chamadas, seis chamadas integradas ao sistema com cada modelo BERT e uma comparação controlada de V2 e V3 com 80 textos por versão (160 chamadas). A V1 foi reanalisada pelos arquivos históricos das autoras; não foram feitas novas chamadas ao GPT-5. Na comparação V2/V3, os mesmos 80 textos, categorias do corpus e pontuação simulada foram usados para ambas as versões.

| Indicador de preenchimento | V2 | V3 |
|---|---:|---:|
| Respostas com campo de base legal bruto preenchido | 57/80 | 40/80 |
| Após o filtro | 55/80 | 40/80 |
| Categoria retornada igual à categoria fornecida | 80/80 | 80/80 |
| Casos “Seguro” em que a base legal ficou vazia | 20/20 | 20/20 |

Esses números contam o que foi preenchido e o que o filtro aceitou. Não medem acurácia de fraude nem provam que uma lei seja aplicável ao caso. V2 e V3 preencheram o campo “Motivo” em todos os casos Seguro, apesar da instrução para deixar campos vazios, mostrando um desvio de instrução. O filtro só verifica correspondência com uma lista permitida; não é uma revisão jurídica. A equipe não realizou novo estudo com participantes nem avaliação jurídica especializada.

### 7. Rever resultados humanos já existentes

A equipe reanalisou formulários de usabilidade e avaliações jurídicas publicados junto aos materiais das autoras; não recrutou novos participantes. A pontuação SUS calculada foi 87,0, e 49 de 72 julgamentos jurídicos foram classificados como pertinentes conforme a regra de análise registrada. Isso é uma reanálise dos dados disponíveis, não uma nova validação independente do produto nem prova de correção legal.

## O que significam as métricas principais

- **Classe/categoria:** grupo que o modelo tenta atribuir a um texto, como phishing ou Seguro.
- **Treino:** exemplos usados para o modelo aprender padrões.
- **Validação:** exemplos usados durante o desenvolvimento para escolher configurações ou quando parar o treinamento.
- **Teste/holdout:** exemplos reservados para medir desempenho depois do ajuste. Se forem usados repetidamente para escolher o modelo, deixam de ser uma avaliação totalmente independente.
- **Fold:** uma das partes de uma validação cruzada. Em cinco folds, cada parte é usada como teste em uma rodada.
- **Acurácia:** proporção de exemplos classificados corretamente. Por exemplo, 31/45 = 68,9%.
- **Precisão:** entre os exemplos que o sistema marcou como uma classe, quantos realmente eram daquela classe.
- **Recall (sensibilidade):** entre os exemplos que realmente pertenciam a uma classe, quantos o sistema encontrou.
- **F1:** combina precisão e recall. O F1-macro calcula o F1 de cada classe e depois tira uma média simples, dando o mesmo peso a classes grandes ou pequenas. É útil quando não se quer que uma classe domine a nota geral.
- **Desvio padrão (±):** indica quanto os resultados variaram entre folds. Não é intervalo de confiança e não prova equivalência entre experimentos.
- **p-valor:** medida de compatibilidade dos dados com uma hipótese estatística, sob certas suposições. p≈0,22 não demonstra que os resultados são iguais; indica que os dados disponíveis não fornecem evidência suficiente de diferença pelo teste aplicado.
- **Confiança softmax:** pontuação interna do classificador convertida em escala semelhante a porcentagem. Sem calibração, não deve ser apresentada como probabilidade real de golpe. No sistema, o campo “risco” deriva dessa pontuação.
- **Token:** unidade de texto processada pelo modelo; pode ser uma palavra ou parte de palavra. Um limite de tokens limita o tamanho processado ou gerado.
- **API:** forma padronizada de um programa pedir um serviço a outro. Neste caso, a API local conecta o navegador ao classificador e às etapas seguintes.
- **JSON:** formato estruturado de dados, com campos e valores, para que a extensão consiga separar motivo, base legal e recomendação.
- **RAG:** sigla de *Retrieval-Augmented Generation*, ou geração com recuperação de contexto. O modelo recebe informação recuperada além do texto do usuário. Neste projeto, a seleção de contexto é por categoria em uma base/dicionário; não é uma busca vetorial sofisticada.
- **Filtro jurídico:** regra que mantém referências reconhecidas em uma lista permitida. Ajuda a limitar saídas, mas não decide se a lei se aplica juridicamente ao caso.
- **SUS:** *System Usability Scale*, questionário padronizado de usabilidade com pontuação de 0 a 100. Uma nota alta descreve a avaliação dos respondentes daquele estudo, não a qualidade da detecção de fraudes.
- **Latência:** tempo entre uma ação e a resposta do sistema.
- **Replicação:** tentativa de executar novamente o método de um estudo para verificar se resultados e funcionamento se mantêm. Uma replicação pode ser parcial se algumas partes diferirem ou não puderem ser refeitas.

## Afinal, o experimento teve o mesmo resultado do original?

**Resposta curta: parcialmente.**

| Parte | Comparação | Conclusão cuidadosa |
|---|---|---|
| Preparação dos splits BERT | 29 arquivos coincidiram byte a byte | Reproduzida com alta fidelidade |
| BERT, validação cruzada | 0,766 contra 0,763 no artigo; quatro folds coincidem com os JSONs das autoras | Muito próximo; não é prova de equivalência total |
| BERT, holdout | 31/45 acertos contra 37/45; F1 0,688 contra 0,828 | Não reproduzido numericamente; a amostra pequena não permite afirmar diferença estatística, nem igualdade |
| Baseline TF-IDF + SVM | 0,703 contra ≈0,67 no artigo e 0,711 no README | Divergência não explicada, mesmo após verificações |
| Fluxo navegador → API → BERT → GPT → filtro → janela | Fluxo completado nos casos testados | Integração demonstrada em ambiente controlado, não desempenho real em escala |
| V2 × V3 | Contagens diferentes de campos legais aceitos | Comportamento medido; não prova qual versão é melhor nem validade jurídica |
| Usabilidade/avaliação jurídica | Dados existentes foram recalculados | Reanálise dos materiais das autoras, sem novos participantes |

Assim, uma forma correta de dizer na apresentação é: **“Reproduzimos a preparação dos dados e obtivemos resultados de validação cruzada do BERT muito próximos aos publicados. O resultado de holdout e o baseline não coincidiram. Também fizemos a integração funcionar em ambiente local. Por isso, classificamos o trabalho como uma replicação parcial e não afirmamos que o sistema esteja validado para uso real.”**

## Limitações que vale mencionar

1. São apenas 450 textos, provenientes de fontes diferentes e em parte traduzidos; os resultados podem não representar a variedade de golpes encontrados hoje.
2. Há duplicatas entre treino e teste em algumas divisões, e o teste do BERT também participa da escolha da época na validação cruzada. Isso pode deixar as métricas mais otimistas.
3. A equipe não conseguiu determinar a causa das divergências no baseline e no holdout. Faltam alguns registros históricos completos das execuções originais.
4. A acurácia publicada do BERT no holdout é baseada em 45 textos; a amostra é pequena e não permite conclusões fortes.
5. O GPT pode produzir explicações ou recomendações inadequadas. Uma resposta em JSON ou uma citação que passou pelo filtro não garante correção factual ou jurídica.
6. Os testes de integração foram locais e controlados; não houve teste com uma conta real do Facebook, usuários novos ou um estudo novo de usabilidade.
7. As análises de V2/V3 são uma geração por entrada e versão. Saídas de modelos de linguagem podem variar; as contagens não demonstram causalidade nem significância estatística.
8. As seis amostras usadas para cobrir categorias na integração não são uma avaliação independente de acurácia.

## Sugestão de roteiro para falar

1. **Problema:** golpes em redes sociais são difíceis de reconhecer; o projeto tenta explicar sinais de risco diretamente no navegador.
2. **Solução:** o BERT classifica o texto e o GPT-4o monta uma explicação e uma recomendação com contexto legal.
3. **Como avaliamos:** conferimos os dados, reproduzimos o baseline e o treinamento BERT, e testamos a extensão/API em ambiente local.
4. **Resultados:** validação cruzada BERT próxima; baseline e holdout diferentes; fluxo integrado concluído nos casos controlados.
5. **Conclusão:** replicação parcial. Funcionamento técnico não equivale a provar que a IA acerta golpes ou que suas recomendações são juridicamente corretas.
6. **Próximos passos sugeridos:** criar divisões de treino/teste sem duplicatas e iguais para os modelos, ampliar e revisar o corpus, avaliar incerteza e pedir revisão humana especializada das recomendações.

## Referências internas para conferir os detalhes

- [Relatório de replicação](../02_relatorios/relatorio_replicacao.md)
- [Validação do treinamento BERT](../02_relatorios/validacao_treinamento_BERT.md)
- [Investigação do baseline](../02_relatorios/investigacao_baseline.md)
- [Validação integrada](../02_relatorios/validacao_integrada.md)
- [Integração com o BERT treinado no Colab](../02_relatorios/integracao_BERT_Colab_GPT4o.md)
- [Comparação V2/V3](../02_relatorios/comparacao_pipelines_GPT4o.md)
- [Índice dos insumos e evidências](../INDICE_INSUMOS.md)
