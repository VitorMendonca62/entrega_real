# Adendo — piloto real GPT-4o com BERT publicado

18 chamadas concluídas, sem erros de API, recusas ou truncamentos. Teto autorizado: US$ 1.
Custo calculado pelos tokens retornados, sem desconto de cache: US$ 0.116973.
Este valor é uma estimativa conservadora de consumo, não uma consulta ao faturamento da conta.
Tokens de entrada: 31329; saída: 3865. Modelo retornado: gpt-4o-2024-08-06.
Preço usado: US$ 2,50/1M entrada e US$ 10/1M saída, conforme https://developers.openai.com/api/docs/models/gpt-4o.

## Escopo

Seis textos de README/sintéticos, três chamadas por texto. As classificações e scores
foram reutilizados da execução real anterior do checkpoint publicado pelas autoras.
Não houve novo treinamento BERT. Não há rótulos independentes validados nem métricas
novas de acurácia, F1 ou validade jurídica. O piloto cobriu 3 categorias preditas:

- Ataques de Phishing e Roubo de Dados: 9 chamadas.
- Golpes de Desinformação Digital: 6 chamadas.
- Golpes Baseados Em Relacionamento: 3 chamadas.

Os seis textos não produziram seis classes distintas. O ramo Seguro não foi coberto
por este lote. Não confundir sucesso técnico de 18/18 com qualidade do sistema.

## Procedimento e diferenças

Prompt, schema JSON e filtro jurídico extraídos do código original. Chamadas diretas
à API oficial; chave lida do .env local, sem inclusão nos logs ou entregáveis.
Foram adicionados limite de 1.200 tokens de saída, timeout de 60 segundos e zero
retries automáticos para controle de gasto. Reservas conservadoras são gravadas antes
de cada chamada para impedir que uma execução interrompida repita cobranças.
Limite conservador de todo o lote: US$ 0,745838.
As respostas brutas, uso de tokens, identificador de modelo, latência e saídas filtradas
estão nos arquivos chamada_00.json a chamada_17.json da pasta de evidências.
O teste executou a composição BERT publicado → prompt → GPT → filtro; não testou
extensão instalada nem a rota HTTP de sucesso de ponta a ponta.

## Caso observado

A mensagem “Bom dia, pessoal! Amanhã tem reunião do condomínio às 19h no salão de festas.”
recebeu a categoria Desinformação pelo BERT. Na primeira resposta, o GPT reconheceu
que não havia evidência explícita de golpe e deixou Base_Legal vazia, mas recomendou
bloquear e denunciar o perfil. Isso evidencia uma inconsistência entre explicação e
recomendação, compatível com a dependência do prompt da categoria predita.
Esta é uma observação qualitativa, não uma avaliação jurídica ou estatística.

## Treinamento

O enunciado solicita treinamento e validação cruzada “quando viáveis”. Utilizar o
checkpoint publicado permite replicar a operação do sistema. Reproduzir os resultados
de treinamento exige executar o protocolo novamente; métricas das autoras continuam
identificadas como resultados publicados/reanalisados. O notebook Colab está preparado,
mas não foi executado em GPU.

Este adendo atualiza a pendência de chamadas GPT do relatório e da apresentação
anteriores. A apresentação foi posteriormente atualizada com este piloto e com a validação integrada descrita em validacao_integrada.md.
