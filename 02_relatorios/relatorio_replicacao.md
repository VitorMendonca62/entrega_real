# VeritaPlugin — Relatório técnico de replicação, Etapa 01

**Data:** 20/10/2026, America/Sao_Paulo. **Revisão:** 20/10/2026 (ver §15). **Equipe:** Vitor Mendonça, Julia Nunes e Luis Felipe. **Apresentação:** data a confirmar.

## 1. Conclusão e escopo

A replicação é **parcial**, com o fluxo funcional completo agora validado. Foram executados o baseline TF-IDF + LinearSVC, regeneração dos splits, auditoria de dados, inferências do checkpoint público, 30 testes determinísticos do filtro, testes HTTP e 190 chamadas reais ao GPT-4o: 18 no piloto, seis integradas com o checkpoint publicado, seis integradas com nosso BERT Colab e 160 na comparação V2/V3 (80 por versão). As seis categorias preditas foram cobertas. Os seis treinamentos BERT foram concluídos no Colab em Tesla T4 e seus artefatos foram recebidos e auditados. O modelo holdout foi carregado e reavaliado localmente, confirmando as métricas da GPU. Não houve novo estudo com participantes.

A investigação comparou scikit-learn 1.5.0/1.5.1/1.5.2, espaços nas extremidades e folds do BERT. A diferença do baseline permaneceu sem causa demonstrada. Relatórios detalhados: [investigacao_baseline.md](investigacao_baseline.md) e [validacao_integrada.md](validacao_integrada.md).

O baseline obteve **F1-macro médio 0,703389 ± 0,027903** (desvio populacional dos cinco folds). A documentação atual informa 0,711 ± 0,027 e o artigo informa aproximadamente 0,67. A divergência permanece sem causa demonstrada. O baseline e o BERT não usam os mesmos folds, apesar da seed comum. Há duas mensagens duplicadas e vazamento textual entre treino e teste em parte dos folds. O novo BERT CV obteve 0,765588 ± 0,036405, numericamente próximo do artigo; **quatro dos cinco folds são idênticos aos JSONs das autoras até a 16ª casa decimal** e só o fold 2 difere (+1,14 pp). O holdout obteve F1 0,688197 contra 0,828 publicado (31/45 contra 37/45 acertos). Com apenas 45 textos, essa diferença de seis acertos **não é estatisticamente significativa** (Fisher exato bicaudal p ≈ 0,22; IC95% Clopper-Pearson da acurácia 53,4%–81,8% nesta execução e 67,9%–92,0% nas autoras); isso indica ausência de evidência de diferença, não equivalência. A diferença descritiva frente ao nosso baseline é cerca de 6,22 pp, contra os 9 pp declarados no artigo, com folds distintos; não confirma a comparação pareada nem a magnitude de ganho descrita no artigo.

**Convenção de origem:** PUBLICADO = PDF do artigo; AUTORES = repositórios/model card; EXECUTADO = novos cálculos, inferências ou testes desta replicação; PENDENTE = não executado. Recalcular respostas dos autores é reanálise, sem novos participantes. Ler JSON de treinamento não é treinar um modelo.

## 2. Fontes e leitura do artigo

Referência: Norões, B. A.; Rocha, B. M. S.; Motta, R. *VeritaPlugin: Uma Extensão de Navegador para Detecção Semântica de Fraudes no Facebook*. SBSeg 2026, 16 páginas. DOI: [10.5753/sbseg.2026.26924](https://doi.org/10.5753/sbseg.2026.26924). A página editorial informa 01/09/2026. O PDF completo foi obtido pela rota `/article/download/44359/44122`, lido por extração de texto e a Figura 3 foi conferida visualmente. O artigo, a página e os códigos estão em `evidencias/autores/`.

O problema é classificar fraudes em texto e oferecer explicações compreensíveis no Facebook. As contribuições declaradas são extensão MV3, integração BERTimbau/RAG/GPT-4o, corpus brasileiro e apoio ao letramento digital (pp. 1–2). O escopo exclui análise de imagens e áudio (p. 7). Não reproduzimos a coleta com personas nem interagimos com usuários da rede.

O pipeline descrito nas pp. 9–11 captura texto, recebe uma requisição FastAPI, classifica com BERTimbau, recupera contexto por chave de categoria, solicita JSON ao GPT-4o e filtra referências legais. A recuperação é um dicionário, sem busca vetorial. A Figura 3 compara V1/GPT-5, V2/RAG e V3/validação por tokens. A comparação é qualitativa, sem benchmark quantitativo controlado no PDF.

O corpus tem 450 registros: cinco classes de fraude e Seguro, 75 por classe. A Tabela 1 (p. 10) discrimina oito origens: Externo 1=65, 2=77, 3=104, 4=36, 5=25, 6=43, 7=36 e Interno=64. As fontes incluem ScamWarners, SMS Spam Collection, Fake News Portuguese, sec-fraudimabr e Fake Reviews. Houve curadoria, tradução automática com revisão manual e amostragem intencional. O PDF não fornece medição de concordância entre anotadores suficiente para validar novamente os rótulos.

O treinamento publicado usa BERTimbau cased, AdamW, taxa 2e-5, batch 16, até quatro épocas, weight decay 0,01, limite 512 tokens, seed 42 e early stopping de paciência 2. A avaliação separa holdout e CV estratificada k=5. No k-fold, o teste também escolhe o checkpoint (p. 11), criando otimismo reconhecido pelas autoras. Resultados publicados: CV F1-macro 0,763 ± 0,034, acurácia consolidada 76%; holdout F1 0,828 e acurácia 82,2% (pp. 12–14).

O PDF reconhece tamanho reduzido, tradução e reutilização do teste para seleção. Avaliação jurídica e usabilidade aparecem como trabalhos futuros (p. 14). Os formulários hoje publicados no GitHub pertencem a um estado adicional dos artefatos, não devem ser retroativamente atribuídos como resultados desse PDF. O banimento de uma persona, descrito no artigo, também não constitui por si evidência causal de direcionamento demográfico dos golpes.

## 3. Inventário e versões

O README principal vincula explicitamente os cinco repositórios complementares, Hugging Face e Kaggle ao mesmo trabalho. Os seis repositórios foram clonados em leitura, com snapshot de HEAD; nenhuma tentativa foi feita de afirmar que HEAD coincide com a versão do experimento original. Kaggle respondeu à consulta pública; usamos as planilhas versionadas no GitHub e não afirmamos equivalência byte a byte com o arquivo do Kaggle.

| Artefato | Commit utilizado | Função |
|---|---|---|
| [evolucao-prompt-RAG](https://github.com/brunanoroes/evolucao-prompt-RAG) | `8ca2f7af7861af6ea95a4d762acd2b73ae6e4c44` | V1–V3 e saídas históricas |
| [Treinamento_TF-IDF-SVM](https://github.com/brunanoroes/Treinamento_TF-IDF-SVM) | `a6d2d0ae0781c6d40d71fa20457d0d0de853a968` | baseline executado |
| [ConteudoExtraVeritaPlugin](https://github.com/brunanoroes/ConteudoExtraVeritaPlugin) | `d0a70c399ed6f4564f02931bcee77b26a69f7f18` | fontes, capturas e formulários |
| [treinamento-BERTimbau](https://github.com/brunanoroes/treinamento-BERTimbau) | `0487415058c0cc087dfba4f151652cca82e7d3e2` | preparação, splits e métricas BERT |
| [VeritaPlugin](https://github.com/brunanoroes/VeritaPlugin) | `101d89bc89c45cf1782eb93fce1693a0c558a8e2` | API, classificador, base e extensão |
| [ReplicaTesteFacebook](https://github.com/brunanoroes/ReplicaTesteFacebook) | `b02a375a092460ed1fc502d0544da5f0995e3d68` | interface local |

Modelo público: [brunanoroes/veritaplugin-bert](https://huggingface.co/brunanoroes/veritaplugin-bert), revisão `d05bc15ad4821dbf629ca9473fc30387299b44de`. Apenas config, tokenizer e safetensors foram baixados. `training_args.bin` não foi desserializado. Os pesos têm 435.734.504 bytes e seu hash consta em `modelo_download.json`. Não são duplicados no pacote.

O model card descreve treinamento com holdout, mas não associa criptograficamente esses pesos a um manifesto dos exemplos de treino nem a um log/checkpoint específico. O script de treinamento salva o modelo holdout, o que é uma pista de origem, não prova do checkpoint publicado. Por isso não calculamos “teste independente” com esses pesos no corpus. A configuração declara Transformers 5.0.0, enquanto o README recomenda 4.44.2. O carregamento em 4.44.2 funcionou, sem resolver essa lacuna de proveniência.

Outros repositórios identificados no README: `scraping-scamwarners`, `tradutor-dataset-phishing`, `extrator-dataset-processed_texts` e `tratamento-dados-golpes-lojas-falsas`, todos sob `github.com/brunanoroes/`. Foram identificados como fontes de coleta/transformação, sem executar scraping ou tradução nesta etapa. A replicação parte do corpus final publicado.

## 4. Ambiente e procedimento

Ambiente isolado em `work/venv`: Python 3.12.3, Linux/Pop!_OS conforme `ambiente.txt`, AMD Ryzen 5 5500U, 6 núcleos/12 threads, cerca de 14 GiB RAM total e 4,4 GiB disponíveis na inspeção inicial. Nenhuma GPU CUDA disponível localmente. O treinamento recebido foi executado externamente em Tesla T4 no Colab. Versões principais: torch 2.4.0+cpu, transformers 4.44.2, numpy 1.26.4, scikit-learn 1.5.2 e pandas 2.2.3. O arquivo `versoes.json` e o lock registram todas as versões efetivas.

A restrição de rede do ambiente bloqueou o clone inicialmente; o download foi refeito com acesso liberado, sem modificar arquivos fora da pasta do projeto. A instalação separou o índice PyTorch CPU e fixou scikit-learn/pandas conforme as séries documentadas. Não houve treinamento reduzido nem alteração de hiperparâmetros para obter números mais próximos. Os scripts dos autores foram examinados antes da execução. O TestClient inicialmente ficou bloqueado pela restrição de rede do ambiente; o teste foi interrompido e reexecutado sem essa restrição, com timeout de 60 segundos, chave removida e modo offline do Hugging Face. Não se atribui esse bloqueio ao produto.

Plano aplicado: (1) inventário e matriz; (2) baseline e auditoria; (3) inferência, API e filtro; (4) reanálises; (5) comparação e apresentação. A matriz completa está em `matriz_replicacao.csv`. Scripts próprios apenas coletam evidências ou preparam compatibilidade local. Os códigos originais permanecem preservados.

## 5. Dados, splits e vazamento

As planilhas brutas do baseline e BERT são iguais em conteúdo e ordem. O preparador BERT remove espaços nas extremidades de nove mensagens; o baseline usa o texto bruto. Assim, o campo `mesmos_dados_baseline_bert=false` da primeira auditoria compara texto bruto com texto já tratado, não duas versões diferentes da planilha. A auditoria complementar esclarece isso.

São 448 textos distintos em 450 linhas, com dois pares duplicados exatos, ambos com rótulos concordantes. Pares nas linhas Excel 78/92 (Financeiro) e 284/286 (Phishing). A normalização de caixa/espaçamento não encontrou duplicatas adicionais; quase duplicatas semânticas não foram auditadas.

| Fold | Teste BERT | Textos comuns treino/teste BERT | Textos comuns treino/teste baseline | Interseção dos testes BERT/baseline |
|---|---:|---:|---:|---:|
| 1 | 90 | 1 | 0 | 16 |
| 2 | 90 | 0 | 2 | 17 |
| 3 | 90 | 1 | 0 | 12 |
| 4 | 90 | 0 | 0 | 16 |
| 5 | 90 | 2 | 2 | 18 |

As interseções usam hashes do texto com `strip`, não índices locais. A cobertura de teste do BERT varia entre 13 e 16 exemplos por classe/fold, e não exatamente 15. Todos os 29 arquivos regenerados são idênticos em bytes aos versionados. O holdout tem **361 treino, 44 validação, 45 teste**, sem texto exato compartilhado entre esses três conjuntos.

A função `relatorio` dos autores compara índices após `reset_index(drop=True)`. Isso imprime interseções artificiais, pois cada split reinicia sua numeração. Nossos hashes demonstram que esse diagnóstico não prova vazamento no holdout. No CV, há vazamento textual real pelas duplicatas, além do uso do teste como validação na seleção do BERT. A estratificação por fonte distribui estilos entre folds, mas não elimina a possibilidade de aprender artefatos da origem.

## 6. Baseline executado

Executamos `treinamento.py` original com TF-IDF (10.000 features, unigramas/bigramas, sublinear_tf), LinearSVC C=1, max_iter=2000 e seed 42. O vetorizador é ajustado dentro de cada fold, portanto não há ajuste global do vocabulário antes do teste. A execução completa levou aproximadamente 0,55 s no temporizador ao redor de `runpy` (inclui leitura do Excel e impressão, exclui importações anteriores do wrapper). Não medimos pico de memória do processo.

| Fold | F1-macro desta execução |
|---|---:|
| 1 | 0.748184 |
| 2 | 0.670105 |
| 3 | 0.684173 |
| 4 | 0.721019 |
| 5 | 0.693465 |

A média dos folds é 0,703389; o F1-macro consolidado é 0,702749. Eles não são a mesma estatística. O F1 ponderado consolidado também é 0,702749, pois os suportes são iguais. Acurácia: 320/450 = 71,1111%. DummyClassifier: F1-macro 0,047619 em cada fold. O desvio dos folds usa `ddof=0`, como o código original, e não é intervalo de confiança ou critério de sucesso da replicação.

| Classe | Precisão | Recall | F1 | Suporte |
|---|---:|---:|---:|---:|
| Ataques de Phishing e Roubo de Dados | 0.7722 | 0.8133 | 0.7922 | 75 |
| Fraudes em Lojas Virtuais Falsas | 0.7000 | 0.7467 | 0.7226 | 75 |
| Golpes Baseados Em Relacionamento | 0.7143 | 0.9333 | 0.8092 | 75 |
| Golpes de Desinformação Digital | 0.6316 | 0.6400 | 0.6358 | 75 |
| Golpes de Ganho Financeiro Ilusório | 0.8615 | 0.7467 | 0.8000 | 75 |
| Seguro | 0.5577 | 0.3867 | 0.4567 | 75 |

A matriz de confusão e todas as 450 predições com fold, linha Excel e hash estão no pacote. “Acerto” significa concordância com o rótulo publicado, sem nova validação factual do conteúdo.

**Análise de erros reais:** tratando as cinco classes de golpe como positivo, houve 46 falsos positivos entre 75 registros Seguro (61,33%) e 23 falsos negativos entre 375 golpes (6,13%). Não confundir erro entre tipos de golpe com falso negativo binário. Exemplos sem identificadores pessoais: linha 220, “Ah, estou assistindo aqui :)”, Seguro classificado como Relacionamento (FP); linha 403, afirmação sobre perda de empregos em dois anos, rotulada Desinformação e classificada Seguro (FN, paráfrase); linha 165, “Haha você é sempre tão convincente.”, Seguro classificado como Seguro (acerto). Textos muito curtos ou retirados de contexto exigem cautela: o rótulo pode depender de informações ausentes no texto. Não reinterpretamos o dataset como verdade jurídica ou factual.

## 7. BERT, API e extensão

**Execução inicial com pesos publicados:** seis textos, três repetições cada, CPU e dois threads PyTorch, seed 42, eval/no_grad, truncamento em 512 tokens. Três textos vêm do teste mínimo do README e três foram escritos para verificar funcionamento, sem rótulos validados. Não são teste holdout nem CV. O mapeamento numérico de seis classes coincide entre preparador, código de inferência e config publicada.

O carregamento do módulo/modelo após importar PyTorch levou 0.716 s. A primeira inferência levou 0.346 s. Nas outras 17, a mediana foi 0,156 s e p95 0,190 s. O cronômetro inclui tokenização, forward, softmax e seleção do rótulo; exclui HTTP, LLM e interface. São textos curtos com caches aquecidos, não benchmark de textos de 512 tokens.

| Texto de teste | Categoria recebida | Confiança softmax |
|---|---|---:|
| exemplo_README_1 | Ataques de Phishing e Roubo de Dados | 0.4566 |
| exemplo_README_2 | Ataques de Phishing e Roubo de Dados | 0.3033 |
| exemplo_README_3 | Golpes de Desinformação Digital | 0.2257 |
| sintetico_relacionamento | Golpes Baseados Em Relacionamento | 0.3293 |
| sintetico_loja | Ataques de Phishing e Roubo de Dados | 0.3635 |
| sintetico_desinformacao | Golpes de Desinformação Digital | 0.2435 |

Nos exemplos do README, prêmio deveria receber Financeiro e condomínio deveria receber Seguro, segundo a expectativa dos autores. Nesta execução receberam Phishing e Desinformação. As confianças foram baixas. Isso aponta incompatibilidade com os exemplos documentados, mas seis textos não sustentam estimativa de acurácia nem permitem identificar a causa. O campo `risco` é `round(score * 100)`: confiança na classe vencedora, inclusive Seguro, sem calibração de probabilidade de fraude. O modal atual nem renderiza esse campo, apesar da descrição no README.

**API real:** health=200, mensagem vazia=400, ausência de chave=401 e corpo sem `message`=422 foram confirmados. Na etapa integrada, seis requisições reais da extensão completaram a rota de sucesso com BERT e GPT-4o, sem mocks. Um wrapper preservou os arquivos originais e instrumentou classificação, geração e controle de gasto. Também foi confirmado erro 502 com geração bloqueada, antes do lote pago.

**Navegador:** após a inspeção inicial no navegador, instalamos Chromium via Playwright e carregamos a extensão MV3 em perfil temporário persistente. Botão, seleção e cancelamento foram confirmados nas páginas originais index, Marketplace e mensagens. Seis textos do corpus foram analisados numa página controlada adicional, atravessando service worker, API, BERT, GPT e modal real. A captura inicial `replica_feed_real.png` continua sendo apenas a réplica; as novas capturas `validacao_integrada/modal_*.png` mostram o fluxo de sucesso.

Os tempos do clique ao modal foram 4,675; 3,273; 2,316; 3,263; 3,444 e 4,069 segundos. O modelo já estava carregado; o primeiro valor é a primeira requisição paga da sessão do navegador, não uma partida a frio. A amostra não sustenta garantia de latência. O teste de seleção confirmou que clicar em um span envia somente seu `innerText`, podendo omitir o restante da publicação. A limitação foi preservada.

**Compatibilidade e fluxo de credenciais:** o manifest original injeta content script apenas em Facebook, não localhost. `background.js` e `setup.js` apontam para Railway. O background transmite `api_key` no JSON ao backend, divergindo da afirmação da p. 8 de que a chave não passa por outro servidor além da OpenAI. Não enviamos chaves a Railway. Foi preparada uma cópia local com host/URLs restritos a 127.0.0.1:8080 e 5500. O patch está preservado e não muda classificador, prompt ou filtro. A cópia foi instalada e testada no Chromium. O teste de onboarding usou uma chave fictícia; na geração real a chave permaneceu no backend, via .env, com o valor do navegador vazio. Não se testou uma chave real armazenada pela extensão.

## 8. RAG e avaliações dos autores

**Código consultado:** contexto por chave exata, instrução de tratar a categoria como imutável, JSON Schema estrito e pós-filtro. O código chama Chat Completions, embora alguns comentários e o artigo mencionem Responses API. Temperatura/seed/max_tokens não estão explicitados na chamada original. O nome `gpt-4o` não fixa snapshot histórico.

**30 testes novos sem LLM:** seis categorias × cinco entradas sintéticas (vazia, desconhecida, permitida, prefixo numérico, mistura). A saída preserva somente nomes cadastrados, mas `Art. 1710` ativa `Art. 171` por substring. A mistura `Art. 171; Art. 9999` remove o artigo desconhecido, porém marca `Lei_Invalida_Detectada=false`. Para Seguro, qualquer citação é descartada. Isso testa o filtro, não mede alucinação do GPT nem adequação jurídica. Nenhuma correção foi implementada.

**Reanálise RAG V2/V3:** ambas as planilhas têm 80 linhas e as mesmas entradas, não cerca de 30 como indicado no README. A amostragem agrupa categoria × origem. V2 possui 53 campos Base_Legal não vazios; V3, 44. Todas as referências filtradas coincidem com nomes permitidos na respectiva base; Seguro está vazio nas 20 linhas de cada versão. Não há erro registrado nas colunas de erro. As saídas brutas anteriores ao filtro não estão preservadas, logo não é possível medir quanto o LLM inventou ou quanto o filtro removeu. A média de caracteres em Desinformação caiu de 34,2 para 13,6, contrariando a expectativa textual do README; comprimento não mede qualidade. Os scripts complementares usam categoria conhecida e score simulado 0,92, e não reproduzem a propagação de erro do BERT no sistema integrado.

**Reanálise SUS:** n=15, média 87,0, DP amostral 11,19, mediana 87,5, mínimo 70, máximo 100; 15 acima de 68. Os dez itens foram convertidos por polaridade: ímpares x−1, pares 5−x, soma ×2,5. Sem valores ausentes ou fora de 1–5. São respostas históricas disponibilizadas pelos autores, sem novo recrutamento. A sequência sem/ com auxílio e a amostra de conveniência não sustentam inferência causal de redução de golpes.

**Reanálise jurídica:** quatro avaliadores × 18 casos = 72 julgamentos por critério. Pertinência plena 49/72 (68,06%); correção 55/72 (76,39%); proporcionalidade 59/72 (81,94%). Apresentaria ao leigo: sim 41/72 (56,94%), com ajustes 24/72 (33,33%), não 7/72 (9,72%). Os 72 julgamentos não são 72 participantes independentes. Não agregamos “com ajustes” a “sim” para afirmar aprovação irrestrita, nem emitimos parecer jurídico próprio.

## 9. Comparação e validade

| Experimento/métrica | Artigo | Referência atual dos autores | Esta execução | Diferença | Comparabilidade / evidência |
|---|---|---|---|---|---|
| Baseline média F1 CV | ≈0,67 | 0,711 ±0,027 | 0,703389 ±0,027903 | −0,7611 pp vs README | Mesmo script atual e sklearn 1.5.2; referência arredondada. `baseline_metricas.json`. Causa não demonstrada |
| Baseline vs artigo | ≈0,67 | — | 0,703389 | +3,34 pp (+5,0% relativo) | Artigo arredondado (“≈0,67”); estado histórico não reconstruído. Diferença indicativa |
| BERT F1 CV | 0,763 ±0,034 | 0,763301 ±0,033743 nos JSONs | 0,765588 ±0,036405 novo treinamento | +0,2588 pp vs artigo arredondado (+0,3% relativo) | Código/splits conferidos; folds 1, 3, 4 e 5 idênticos aos das autoras, fold 2 +1,14 pp |
| Ganho BERT − baseline (F1 CV) | ≈9 pp | — | 6,22 pp | −2,78 pp | Folds diferentes entre BERT e baseline; descritivo |
| BERT holdout | 0,828 / 82,2% | 0,828041 / 82,2222% (37/45) | 0,688197 / 68,8889% (31/45) | −13,98 pp F1 (−16,9% relativo) | Reavaliação CPU confirmou 31/45. n=45: Fisher p≈0,22, ICs sobrepostos; sem significância estatística e sem causa estabelecida |
| SUS | Trabalho futuro | 87,0, n=15 | 87,0, n=15, reanálise | 0 ponto SUS | Mesmos dados e fórmula; `sus_reanalise.json` |
| Pertinência jurídica | Trabalho futuro | 49/72 | 49/72, reanálise | 0 pp | Mesmos julgamentos; `juridico_reanalise.json` |
| Latência integrada | Sem benchmark numérico | 2–4 s | 2,316–4,675 s (checkpoint publicado, n=6); 2,686–4,526 s (BERT Colab, n=6) | Não é teste de equivalência | Extensão real; modelo carregado; 80–90% do tempo (mediana) é a chamada GPT-4o (`latencias_integradas.csv`) |
| V2/V3 com base legal após filtro | Qualitativa (Figura 3) | 80 linhas por versão | V2 55/80; V3 40/80; Seguro 0/20 em ambas | Não calculada | 160 chamadas reais; mudança de prompt, base e filtro ao mesmo tempo |
| Inferência BERT | Sem benchmark numérico | <200 ms | Mediana 156 ms, 17 execuções após primeira | Não calculada | Hardware/textos distintos; não valida limite geral |

O −0,7611 pp expressa `(0,703389−0,711)×100`, não variação relativa. O log original imprime uma diferença em escala 0–1 seguida de “pp”; essa unidade é incorreta e o BERT ali é constante hardcoded, não foi treinado pelo script. Não usamos essa linha como resultado novo ou como comparação pareada.

A reprodução de 29 arquivos de split é evidência forte de compatibilidade da preparação atual, mas não elimina vazamento de duplicatas nem viés de seleção. O dataset pequeno, heterogêneo e parcialmente traduzido limita validade externa. As inferências curtas não provam qualidade em produção; o teste de filtro não substitui avaliação semântica. Não há identificação da versão histórica do GPT, nem rastro completo que vincule pesos a exemplos. As discrepâncias do README não foram “corrigidas” para forçar concordância.

## 10. Propostas para a Etapa 02 (não implementadas)

| Prioridade / proposta | Problema e evidência | Mudança sugerida e hipótese | Experimento e sucesso proposto | Esforço, recursos e riscos |
|---|---|---|---|---|
| **1. Splits independentes e comuns** | Duplicatas cruzadas, folds diferentes e teste usado para early stopping | IDs persistentes, grupos de duplicatas, manifesto comum e validação interna. Hipótese: estimativa menos otimista e comparação atribuível ao modelo | Retreinar baseline e BERT com mesmos testes externos e validação interna. Zero interseções por grupo; reportar F1 por fold, recall Seguro e incerteza, sem exigir ganho de F1 | 3–5 dias, GPU disponível sem custo ou orçamento separado. Dataset pode ficar pequeno por grupo |
| **2. Validação de citações por identificador** | Art. 1710 reconhecido como 171; flag ignora misturas | Reconhecer número/código completo, limites de token e registrar cada rejeição. Hipótese: reduzir falsos reconhecimentos | Conjunto de regressão com abreviações, artigos adjacentes e misturas. Zero aceitações de IDs inválidos, recall ≥95% das variantes válidas definidas antes do teste | 2–3 dias, CPU, até 3 estudantes. Risco de rejeitar abreviações legítimas; nenhuma alegação de correção jurídica |
| 3. Tratamento explícito da incerteza | Softmax chamado risco; prompt força categoria; FP em Seguro | Calibrar confiança em validação separada e permitir abstenção/explicação de incerteza. Hipótese: reduzir alertas indevidos | Comparar FPR e FNR binários, ECE/Brier e cobertura. Meta inicial: reduzir FPR em ≥20% relativo sem elevar FNR em mais de 2 pp; metas a pré-registrar | 4–7 dias, validação adicional. Menor cobertura e risco de segurança por abstenção |
| 4. Corpus nativo e controle de fonte | Fontes heterogêneas e textos curtos sem contexto | Expandir Seguro e golpes com contexto, anotação dupla e divisão temporal/por fonte | Concordância, macro-F1 e recall Seguro em conjunto externo. Meta: elevar recall Seguro em ≥5 pp sem perda >2 pp no macro-F1 | 1–2 semanas ou mais, coleta ética e anotadores. Maior esforço e risco de privacidade |

As duas primeiras são prioritárias para uma equipe de até três estudantes. Não são apresentadas como ganhos já obtidos. Expansão do corpus e avaliação humana já são previstas pelas autoras; a contribuição proposta é operacionalizar protocolos e critérios, não reivindicar novidade conceitual. Nenhuma melhoria foi implementada nesta etapa.

## 11. Pendências e entrega

1. Equipe: Vitor Mendonça, Julia Nunes e Luis Felipe. Data da apresentação a confirmar.
2. **Concluído:** seis treinamentos Colab, auditoria e reavaliação local. CV próxima e holdout divergente; investigação causal suspensa por decisão da equipe.
3. **Pendente histórico:** vínculo completo entre pesos, inicialização, ambiente e resultados das autoras; nenhum contato foi realizado pela equipe de execução.
4. **Concluído:** 190 chamadas GPT-4o no total, incluindo 160 V2/V3 e seis novas integradas. V1 somente reanalisada, sem chamadas GPT-5. Consumo total conservador US$ 1.023203 dentro do teto agregado US$3; acesso pago fechado.
5. **Concluído:** extensão MV3 e seis casos com o checkpoint publicado; nova integração de seis casos com nosso BERT Colab. Seleção/cancelamento também verificados nas três páginas originais da réplica. Não equivale a uma validação em conta Facebook real.
6. **Concluído:** ZIP Colab conferido, checkpoint separado e seis modais reais com nosso modelo. As evidências dos dois checkpoints continuam separadas.
7. **Concluído:** V2/V3 reexecutadas, 80 entradas por versão, amostra regenerada idêntica às planilhas. Prompts, bases, schemas e filtros preservados; categoria do corpus e score 0,92. Ausência de limite explícito de saída preservada; retries desativados, timeout de 90 s e reserva de custo são adaptações. Diferenças históricas não foram eliminadas.

O pacote contém materiais dos autores separados de resultados desta replicação. Os originais podem conter dados de terceiros e URLs de golpes; não foram acessados. A apresentação usa resultados agregados e exemplos sem identificadores. Os scripts, hashes, instruções e índice permitem auditar a proveniência. O relatório IEEE e a implementação de melhorias não fazem parte desta entrega.

## 12. Evidências da validação adicional

Nas condições testadas, versões 1.5.x do scikit-learn e espaços nas extremidades não explicam a divergência. A troca de folds também não recupera os valores declarados. A causa permanece não estabelecida. Seriam necessários os logs, ambiente e entradas exatos que produziram o número publicado para determinar sua origem. Não há evidência para atribuir erro às autoras ou declarar equivalência estatística.

O histórico do baseline foi recuperado sem mudar o checkout. Relatórios e resultados estruturados estão nas pastas investigacao_baseline/ e validacao_integrada/. O wrapper mantém os quatro módulos originais idênticos por hash. Nenhuma melhoria metodológica ou correção do extrator/filtro foi incorporada.

## 13. Treinamento recebido do Colab

Os seis treinamentos foram executados com script original idêntico, alterando somente o caminho da revisão base. Os 29 arquivos de split e o manifesto de entradas coincidem com os autores. Status complete, retorno zero, seis resumos de quatro épocas e GPU Tesla T4 foram confirmados.

A média CV nova é 0,765588 ± 0,036405, enquanto o consolidado é F1 0,764904 e acurácia 76,4444%. No holdout, o F1 é 0,688197 e a acurácia 68,8889%, reproduzidos localmente em CPU com 31/45 acertos. A proximidade CV e a divergência holdout devem ser apresentadas juntas. Não se deve concluir reprodução de 100% por sobreposição de desvios padrão.

Comparando fold a fold com os JSONs das autoras, os folds 1, 3, 4 e 5 coincidem até a 16ª casa decimal (diferença < 10⁻¹²); apenas o fold 2 difere (0,810974 contra 0,799536). Portanto, com o mesmo script, splits e versões, o treinamento foi reproduzido de forma praticamente exata em quatro de seis execuções. Fold 2 e holdout divergem. Uma hipótese compatível, **não verificada**, é que os valores publicados para essas duas execuções venham de uma rodada diferente da que gerou os demais folds. Também não se pode descartar a variação não determinística da GPU nessas execuções. Sem as predições por exemplo das autoras, não é possível um teste pareado; o teste de Fisher (p ≈ 0,22) é a comparação disponível e não mostra diferença significativa. Detalhes: `03_insumos/tabelas/bert_treinamento_colab/folds_nova_execucao_vs_autoras.csv` e `holdout_teste_estatistico.json`.

O script original não fixa explicitamente a seed antes da primeira construção da cabeça de classificação e não salva os modelos/predições brutas dos cinco folds. Essas limitações foram preservadas; são hipóteses e limites de auditabilidade, não causas demonstradas para a diferença holdout. Detalhes em [validacao_treinamento_BERT.md](validacao_treinamento_BERT.md). O ZIP original, com pesos, está preservado separadamente como treinamento_BERT_Colab_original.zip.

## 14. Comparação final V2/V3 e integração do novo BERT

V1 foi reanalisada em 450 respostas históricas, sem GPT-5. V2/V3 foram reexecutadas em 80 pares de entradas, categoria do corpus e score simulado 0,92; não usam as previsões BERT. Todas as 160 chamadas concluíram com JSON válido, categoria fornecida preservada e modelo retornado `gpt-4o-2024-08-06`. V2 teve 57 campos legais brutos e 55 filtrados preenchidos; V3 teve 40 antes e depois. Seguro manteve base legal vazia em 20/20 por versão, mas ambas preencheram Motivo em 20/20, apesar da instrução de campos vazios. Esses resultados medem conformidade e comportamento, não validade jurídica nem ganho atribuível apenas ao prompt.

O sistema completo foi testado em seis textos do holdout selecionados pela categoria predita do modelo Colab. Todos passaram pela extensão, API, BERT, GPT, filtro e modal; tempos de clique até modal entre 2,686 e 4,526 s, com modelo já carregado. O sucesso técnico foi 6/6, mas houve concordância com o rótulo do corpus em 4/6; o exemplo predito Seguro era Relacionamento no corpus. Essa seleção cobre classes e não constitui uma nova avaliação independente de generalização.

Detalhes, respostas brutas, campos, tokens, tempos e limitações: [comparacao_pipelines_GPT4o.md](comparacao_pipelines_GPT4o.md) e [integracao_BERT_Colab_GPT4o.md](integracao_BERT_Colab_GPT4o.md). O lote final teve 166 chamadas; o total histórico é 190. O orçamento agregado ficou em US$ 1.023203, sem desconto de cache. Acesso pago fechado, serviços encerrados e perfil temporário removido. Não se declara reprodução exata de 100%: holdout e baseline divergem e faltam informações históricas. Nenhuma correção metodológica foi implementada.

## 15. Revisão da entrega e insumos complementares

Esta cópia do relatório foi revisada em 20/10/2026 sobre o pacote da execução. As alterações foram: (a) cálculo da diferença do baseline contra o artigo e do ganho BERT − baseline; (b) teste estatístico do holdout e registro dos folds idênticos; (c) linhas de latência do BERT Colab e de V2/V3 na tabela da §9; (d) limpeza de linhas vazias e correção do nome da equipe. Os números da execução não foram alterados.

**Caminhos:** este relatório cita os caminhos do layout original (`evidencias/execucao/...`). Na pasta `entrega real`, os arquivos foram reorganizados por tipo (logs, amostras, modelos, imagens, tabelas, scripts, ambiente). A correspondência de cada arquivo está em `03_insumos/tabelas/_controle/mapa_caminhos.csv`.

**Insumos gerados na revisão** (todos derivados dos dados da execução, sem novas chamadas pagas nem novo treinamento):

| Arquivo em `03_insumos/` | Conteúdo |
|---|---|
| `tabelas/comparacao/resumo_metricas.csv`, `imagens/comparacao/artigo_vs_replicacao.png` | Artigo × autoras × replicação, em pp e variação relativa |
| `tabelas/bert_treinamento_colab/folds_nova_execucao_vs_autoras.csv` e `.png` | Comparação fold a fold |
| `tabelas/bert_treinamento_colab/holdout_teste_estatistico.json` | Fisher exato, ICs Clopper-Pearson e erros binários do holdout |
| `tabelas/bert_treinamento_colab/holdout_matriz_confusao.csv`, `holdout_metricas_por_classe.csv`, `holdout_erros.csv`, `imagens/.../holdout_matriz_confusao_recalculada.png` | Holdout por classe e erros (hash, sem texto) |
| `tabelas/baseline_tfidf_svm/baseline_folds.csv`, `baseline_metricas_por_classe.csv`, `baseline_resumo_erros.csv`, `baseline_erros.csv` | Baseline em CSV, incluindo FP/FN |
| `tabelas/extensao_integrada/latencias_integradas.csv`, `latencias_resumo.csv`, `imagens/.../latencias_integradas.png` | 12 fluxos completos decompostos em BERT, GPT e restante |
| `tabelas/gpt4o_custos/custos_gpt4o_por_lote.csv` | 190 chamadas, US$ 1,0232 estimados |
| `tabelas/gpt4o_v1_v2_v3/v2_v3_por_categoria.csv`, `imagens/.../v2_v3_base_legal_por_categoria.png` | V2 × V3 por categoria |
| `tabelas/reanalise_sus_juridico/juridico_contagens.csv`, `imagens/.../sus_escores.png`, `juridico_avaliacao.png` | Reanálises dos dados das autoras |
