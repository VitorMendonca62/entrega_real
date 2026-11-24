# Comparação dos pipelines V2 e V3 e referência V1

**V2 e V3 foram reexecutadas em todos os 80 exemplos de cada versão, totalizando 160 chamadas reais ao GPT-4o.** V1 foi somente reanalisada a partir dos artefatos publicados: nenhuma chamada ao GPT-5 foi realizada.

## Protocolo conferido

A amostra foi regenerada com cinco exemplos por combinação categoria/origem, `random_state=42`, totalizando 80 por versão. Texto, categoria, origem e ordem coincidem exatamente com as planilhas versionadas. O README estima cerca de 30 exemplos, mas o agrupamento efetivo tem 16 grupos e gera 80. Não reduzimos a amostra.

As duas versões receberam os mesmos textos, o rótulo do corpus e score simulado 0,92, preservando o procedimento original. A classificação BERT não foi usada nesta comparação isolada. Cada versão manteve seu prompt, base, schema JSON estrito e filtro. As funções foram extraídas do código original; não foram corrigidas. O manifesto e os hashes das fontes estão nas evidências.

Usamos Chat Completions com `model="gpt-4o"`, sem acrescentar temperatura, seed ou limite explícito de saída. A versão retornada foi registrada por chamada. A ordem foi pareada, V2 e V3 para cada entrada. As adaptações foram leitura da chave local, retries desativados, timeout de 90 s, instrumentação e controle de gasto. Não houve seleção de respostas ou repetição para melhorar resultados.

## Resultados objetivos

| Indicador | V2 | V3 |
|---|---:|---:|
| Chamadas concluídas | 80 | 80 |
| Base legal bruta preenchida | 57 | 40 |
| Base legal filtrada preenchida | 55 | 40 |
| Indicador original de lei inválida | 2 | 0 |
| Categoria retornada igual à fornecida | 80 | 80 |
| Casos Seguro | 20 | 20 |
| Seguro com Motivo preenchido | 20 | 20 |
| Seguro com base legal bruta preenchida | 0 | 0 |
| Seguro com base legal filtrada preenchida | 0 | 0 |

| Categoria | Média de caracteres legais após filtro — V2 | V3 |
|---|---:|---:|
| Ataques de Phishing e Roubo de Dados | 99.60 | 40.40 |
| Fraudes em Lojas Virtuais Falsas | 119.47 | 70.93 |
| Golpes Baseados Em Relacionamento | 70.20 | 15.20 |
| Golpes de Desinformação Digital | 38.00 | 10.60 |
| Golpes de Ganho Financeiro Ilusório | 79.47 | 62.73 |
| Seguro | 0.00 | 0.00 |

Essas contagens descrevem comportamento, não acurácia ou validade jurídica. O indicador do filtro só acusa certos casos sem referência aceita; ele não detecta necessariamente misturas de referências válidas e inválidas. Saídas filtradas reconstruídas com os nomes permitidos demonstram consistência com a base, não pertinência da lei ao fato.

Quantidade de citações, tamanho da explicação ou preenchimento de campos não são medidas automáticas de qualidade. As mudanças entre versões incluem prompt, base e filtro; não podem ser atribuídas somente à redação do prompt. As respostas são estocásticas e há uma geração por entrada/versão: não há teste de significância, causalidade isolada do prompt ou certificação jurídica.

Os 80 pares estão em `pares_comparados.json`, com citações brutas/filtradas, explicações e ações lado a lado. O CSV contém indicadores por caso, tokens, latência e custo. As respostas completas e os prompts efetivamente enviados estão na pasta chamadas/.

## Referência V1 sem GPT-5

Foram reanalisadas 450 linhas publicadas, com 449 motivos, 449 ações e 189 campos legais preenchidos. As entradas e sua ordem coincidem entre as duas planilhas V1. A base é diferente e tem distribuição por categoria distinta de V2/V3; não é uma comparação pareada de três modelos/prompts.

O mapeamento literal de categorias da V1 não reconhece “Golpes Baseados Em Relacionamento” (75 linhas): o código espera outra grafia, com “Relacionamento Romântico”. Seguro também não está no mapa (72 linhas), compatível com uma categoria sem leis, mas sem um ramo equivalente ao das versões posteriores. Isso é uma observação estática do código, não uma reexecução da V1 nem prova de que essa foi a causa de cada saída histórica. A V1 foi mantida como referência conforme orientação do README e instrução do usuário.

## Modelo e consumo

- V2: modelo retornado ['gpt-4o-2024-08-06']; 91480 tokens de entrada e 14730 de saída; custo calculado sem desconto de cache US$ 0.376000.
- V3: modelo retornado ['gpt-4o-2024-08-06']; 129325 tokens de entrada e 13690 de saída; custo calculado sem desconto de cache US$ 0.460213.

Somando o piloto anterior, a primeira integração, a integração com o novo BERT e esta comparação, o total calculado sem desconto de cache foi **US$ 1.023203**, abaixo do teto agregado de US$3. Trata-se de estimativa conservadora pelos tokens, não consulta ao faturamento. O limite de saída de 16.384 tokens foi usado apenas para reservar o custo máximo antes de cada requisição; não foi enviado como parâmetro. Preço de referência: https://developers.openai.com/api/docs/models/gpt-4o. Gate encerrado; próximas chamadas exigem nova solicitação.

## Campos e referências antes/depois do filtro

| Indicador literal | V2 | V3 |
|---|---:|---:|
| Motivo bruto preenchido | 80 | 80 |
| Ações brutas preenchidas | 80 | 80 |
| Motivo filtrado preenchido | 80 | 80 |
| Ações filtradas preenchidas | 80 | 80 |
| Base bruta contendo nome permitido completo | 55 | 40 |
| Base bruta preenchida sem nome permitido completo | 2 | 0 |
| Saídas filtradas só com nomes completos permitidos ou vazias | 80 | 80 |

A comparação literal de nomes completos não reconhece todas as abreviações: ausência de correspondência não significa referência inventada. A base permitida é a da própria versão e categoria. As saídas brutas e filtradas completas permitem revisão posterior.

Exemplos rastreáveis de inconsistência:

- V2, caso 28, `f5f758a6a476975127e4709dd6a54312ae878f77b52eaabc5497b1ada39bae20`: Referência bruta sem reconhecimento pelo filtro; isso não é parecer jurídico. Base bruta: “Art. 171 do Código Penal, Lei nº 14.155/2021”. Base filtrada: “(vazia)”.

- V2, caso 52, `48c2ba493eac25ac555c2f2d9991ebc7d397e47f23cbf96b7b686060fff19e7d`: Referência bruta sem reconhecimento pelo filtro; isso não é parecer jurídico. Base bruta: “Art. 171 do Código Penal; Lei nº 14.155/2021”. Base filtrada: “(vazia)”.

- V3, caso 60, `aa7dc1286c1a7ead86aa03e6d5e300cde42b5563dc18599b29822bbdb7680927`: Motivo preenchido para Seguro apesar da instrução de campos vazios. Base bruta: “(vazia)”. Base filtrada: “(vazia)”.

Os casos Seguro com motivo preenchido são um desvio de instrução; não se trata de um diagnóstico de risco independente. Detalhes em `auditoria_campos_referencias.json`.
