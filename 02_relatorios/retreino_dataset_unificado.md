# Retreino do BERTimbau com o dataset unificado — relatório

*16/11/2026 · dataset: `BrScamsFacebook_Unificado_2.xlsx` (sha256 `b5d89600…4014`) · seed 42 em tudo*

> **Situação (17/11):** os 33 treinos rodaram no Colab (Tesla T4, 16/11, 2h20 no total, determinismo ligado,
> hashes dos dados conferidos). **Veredito: não exportar ainda.** O modelo novo é significativamente melhor que o
> mesmo pipeline com os dados antigos, mas não passa no critério 5 e ainda erra demais na classe Seguro (seção 6).
> O modelo candidato está em `candidato/modelo_candidato/`, no formato do plugin. **Nada foi substituído.**

## 1. Resumo

**Resultado do retreino (Facebook, fora da amostra, 60 mensagens):**

| Modelo | Acurácia | F1 macro | F1 Seguro | Alarme falso | Golpe perdido |
|---|---:|---:|---:|---:|---:|
| Atual no plugin (⚠ ~90% visto no treino) | 0,617 | 0,619 | 0,500 | 0,50 | 0,08 |
| A — mesmo pipeline, dados antigos | 0,400 | 0,399 | 0,308 | 0,75 | 0,06 |
| **B — dataset unificado (novo)** | **0,550** | **0,532** | **0,435** | **0,38** | **0,19** |
| C — unificado sem sintéticos | 0,450 | 0,469 | 0,462 | 0,25 | 0,23 |

- **O dataset novo ajuda:** B − A = +0,15 de acurácia e +0,13 de F1 macro (IC 95% +0,03 a +0,24; McNemar
  p = 0,022). Melhora em todas as classes, e o alarme falso cai pela metade.
- **Mas não basta:** F1 Seguro 0,43 (IC 0,14–0,67), longe do objetivo. As mensagens de golpe classificadas como
  seguras subiram de 6% para 19%.
- **O modelo continua aprendendo o estilo da fonte:** ao tirar uma fonte inteira, a acurácia nela cai para
  0,09–0,63 (B) e 0,00–0,02 (A).

A seguir, os achados da análise do dataset e da linha de base, anteriores ao treino:

1. **O modelo atual do plugin está pior do que parece.** O plugin usa o checkpoint publicado
   `brunanoroes/veritaplugin-bert` (conferido por sha256). Nas 60 mensagens do Facebook ele acerta 61,7%,
   com **F1 Seguro 0,50**, e isso com ~90% dessas mensagens vistas no treino. Em mensagens reais que ele nunca viu
   (n = 141), a acurácia cai para **42,6%** e **48 de 59 mensagens seguras (81%) viram alerta de golpe**.
2. **No dataset novo, a classe ainda é muito previsível pela fonte.** Sete das nove fontes reais têm uma classe
   dominante acima de 67%, e quatro têm uma única classe. Só de saber a fonte já se acerta 56% (NMI 0,45). Por isso a
   validação leave-one-source-out faz parte do protocolo.
3. **O teste do Facebook é pequeno.** São 60 mensagens após deduplicação, só **8 seguras**. Uma mensagem segura a
   mais ou a menos muda o F1 Seguro em ~0,06–0,12. Diferenças pequenas entre modelos não serão conclusivas; o
   relatório traz intervalos de confiança e teste de McNemar.
4. A decisão de exportar segue cinco critérios **fixados antes dos resultados** (seção 5).

## 2. Análise do dataset

### 2.1 Classes e fontes

756 linhas, 6 classes. Após deduplicação: **751**.

| Classe | Total | Facebook | Sintético |
|---|---:|---:|---:|
| Seguro | 161 | 8 | 35 |
| Financeiro | 155 | 14 | 35 |
| Relacionamento | 110 | 10 | 35 |
| Loja Falsa | 110 | 8 | 35 |
| Desinformação | 110 | 5 | 35 |
| Phishing | 110 | 19 | 35 |

| Fonte | Origem | Idioma | n | % |
|---|---|---|---:|---:|
| Dados Sintéticos | gerados | PT (gerado) | 210 | 27,8 |
| Externo 3 | Kaggle Fake News PT | nativo PT | 104 | 13,8 |
| Telegram/Wpp Dataset | Telegram/WhatsApp (novo) | nativo PT | 96 | 12,7 |
| Externo 2 | SMS Spam Collection | traduzido EN→PT | 77 | 10,2 |
| Externo 1 | ScamWarners Romance | traduzido EN→PT | 65 | 8,6 |
| **Interno** | **Facebook (personas)** | nativo PT | **64** | **8,5** |
| Externo 6 | Kaggle Fake Reviews | traduzido EN→PT | 43 | 5,7 |
| Externo 7 | ScamWarners Online Selling | traduzido EN→PT | 36 | 4,8 |
| Externo 4 | sec-fraudimabr WhatsApp/Telegram | nativo PT | 36 | 4,8 |
| Externo 5 | ScamWarners Financial | traduzido EN→PT | 25 | 3,3 |

Real: 546 (72%). Sintético: 210 (28%). O domínio-alvo (Facebook) é só 8,5%.

### 2.2 Matriz fonte × classe

| Fonte | Desinf. | Financ. | Loja F. | Phish. | Relac. | Seguro | Classe dominante |
|---|---:|---:|---:|---:|---:|---:|---:|
| Dados Sintéticos | 35 | 35 | 35 | 35 | 35 | 35 | 17% |
| Externo 1 | | | | | 65 | | **100%** |
| Externo 2 | | | | 56 | | 21 | 73% |
| Externo 3 | 70 | | | | | 34 | 67% |
| Externo 4 | | 36 | | | | | **100%** |
| Externo 5 | | 25 | | | | | **100%** |
| Externo 6 | | | 31 | | | 12 | 72% |
| Externo 7 | | | 36 | | | | **100%** |
| Interno (Facebook) | 5 | 14 | 8 | 19 | 10 | 8 | 30% |
| Telegram/Wpp | | 45 | | | | 51 | 53% |

- **NMI fonte–classe = 0,446**. Um "classificador" que só olha a fonte acerta **56,1%**.
- Só o Facebook e os sintéticos cobrem as seis classes. Os sintéticos são a única fonte totalmente balanceada,
  o que ajuda a desacoplar fonte e classe.
- **De onde vem o Seguro:** Telegram/Wpp 51, sintético 35, Externo 3 34 (notícias verdadeiras), Externo 2 21
  (SMS traduzido), Externo 6 12 (avaliações traduzidas), **Facebook 8**. Só 5% das mensagens seguras têm o estilo do
  Facebook. Isso explica boa parte da fraqueza dessa classe no uso real.
- **Viés de comprimento:** em quase todas as fontes, a mensagem segura é mais curta que o golpe da mesma fonte (mediana
  geral 103 caracteres, contra 163–300 em quatro das cinco classes de golpe; Desinformação tem 85). O modelo pode usar "curto = seguro" como atalho.
- **Emoji:** aparecem em 44–46% das mensagens do Facebook, do Telegram e do Externo 4, contra 0–1% nas fontes
  traduzidas. É mais uma marca de estilo da fonte.

### 2.3 Textos traduzidos

246 linhas (32,5%) vêm de fontes em inglês traduzidas automaticamente (Externo 1, 2, 5, 6 e 7). Não sobrou inglês
literal (nenhum texto com ≥ 10% de palavras em inglês). O problema é de **acoplamento**: entre os dados reais,
"tradutês" é praticamente a marca de três classes.

| Classe (só reais) | % traduzido |
|---|---:|
| Loja Falsa | 89% |
| Relacionamento | 87% |
| Phishing | 75% |
| Seguro | 26% |
| Financeiro | 21% |
| Desinformação | 0% |

### 2.4 Duplicatas e quase-duplicatas

O critério combina texto normalizado igual com cosseno de n-gramas de caractere ≥ 0,85, agrupado em componentes
conexos. As duplicatas foram removidas **antes** de qualquer separação de treino e teste
(`dados_retreino/dedup_removidos.csv`).

| Achado | Linhas |
|---|---:|
| Duplicatas exatas | 3 (uma com rótulos conflitantes) |
| Pares quase-duplicados (cos ≥ 0,85) | 4 |
| **Removidas** | **5**: 3 quase-duplicatas (2 do Facebook, 1 do Externo 4) e 2 linhas do Facebook que eram só uma URL de dataset, com rótulos diferentes |
| Clusters misturando real e sintético | 0 |
| Sintético × real: maior cosseno (mediana) | 0,12. Nenhum sintético é cópia de um real |

O Facebook passou de 64 para **60** mensagens. Por classe: Phishing 17, Financeiro 13, Relacionamento 10,
Loja Falsa 8, Seguro 8, Desinformação 4.

A aba **Candidatos** (144 linhas, 140 de Financeiro) não entrou no treino: não está na Página1 e desbalancearia
ainda mais o Financeiro.

## 3. Linha de base: o modelo atual do plugin

A pasta `work/api_local/modelo_bert` é byte a byte o checkpoint publicado `brunanoroes/veritaplugin-bert`
(revisão `d05bc15a`, sha256 `92d27c9c…`). O plugin roda esse modelo, não as nossas replicações do Colab. Ele foi
rodado agora sobre todo o dataset (`baseline/pred_plugin_publicado.csv`).

| Conjunto | n | Visto no treino? | Acurácia | F1 macro | F1 Seguro |
|---|---:|---|---:|---:|---:|
| Facebook (todas) | 60 | ~90% sim | 0,617 | 0,619 | **0,500** (recall 4/8) |
| Facebook do teste original | 6 | não | 0,500 | 0,467 | 0,667 |
| **Reais inéditos** (teste original + Telegram/Wpp) | 141 | não | **0,426** | 0,442 | **0,301** |
| Telegram/Wpp | 96 | não | 0,240 | — | — |
| Sintéticos (diagnóstico, não é teste) | 210 | não | 0,605 | 0,557 | 0,494 |

*"Visto" = texto presente no treino ou na validação do holdout do repositório das autoras. As autoras não documentam
o conjunto exato usado no checkpoint publicado.*

Matriz no Facebook (linhas = verdadeiro; colunas = Relac., Financ., Phish., Loja F., Desinf., Seguro):

```
Relacionamento  9  0  0  0  0  1
Financeiro      1  6  6  0  0  0
Phishing        0  1 11  2  1  2
Loja Falsa      0  3  1  3  0  1
Desinformação   0  0  0  0  4  0
Seguro          2  0  1  0  1  4
```

**Principais erros do modelo atual:**
- **Mensagens seguras viram golpe.** Nos reais inéditos, das 59 mensagens seguras: 25 viram Desinformação,
  11 Phishing, 10 Relacionamento e só 11 ficam como Seguro. No Telegram/Wpp, 46 de 51 erram. São notícias e avisos
  legítimos ("Saque-aniversário do FGTS…", "Polícia Federal faz operação…", "Em 2021 o Banco Central se tornou
  autônomo…") que o modelo chama de desinformação ou phishing.
- **Financeiro ↔ Phishing** no Facebook (6 casos): "plataforma pagando", "recompensas para novos jogadores".
- **Loja Falsa → Financeiro** (3 casos): "Compro Bradesco Net empresa aprovado…".
- **Confiança baixa:** a probabilidade máxima tem mediana 0,35 (com 6 classes). O modelo raramente está seguro do
  que diz, e acertos e erros têm confiança parecida (0,40 contra 0,30).

Para comparação, as replicações do Colab (20/10 e 26/10) ficam em acurácia 0,617 e F1 Seguro 0,67 / 0,63 no
mesmo conjunto vazado. Não sei de qual medição vem o F1 Seguro 0,64 citado como "atual". Se foi do holdout das autoras, aquele teste
também orientou a escolha da época. Fora da amostra, o modelo do plugin fica bem abaixo disso (0,30).

## 4. Protocolo do retreino

Mesmo pipeline das autoras: `neuralmind/bert-base-portuguese-cased`, lr 2e-5, batch 16, até 4 épocas,
weight decay 0,01, 512 tokens, early stopping com paciência 2, melhor época por F1 macro. O ambiente é o do notebook
v3: Python 3.12 isolado, torch 2.4.0 cu121, transformers 4.44.2, revisão do modelo base registrada.

Diferenças deliberadas, iguais em todos os braços:
1. A época é escolhida numa **validação** de 10% do treino, só com dados reais, e nunca no teste. No artigo, o teste
   orientava a escolha da época, o que gerava um viés otimista.
2. O padding é dinâmico. É equivalente ao `max_length`, porque a atenção mascara o padding, e é mais rápido.
3. Determinismo completo ligado (`enable_full_determinism(42)`).

**Braços** (todos deduplicados):

| Braço | Dados de treino | Papel |
|---|---|---|
| A | 445 originais | linha de base justa: mesmo código, dados antigos |
| **B** | **751 unificados** | **modelo novo** |
| C | 541 unificados sem sintéticos | ablação dos sintéticos |

**Avaliações:**
- **Facebook-CV:** as 60 mensagens do Facebook em 5 folds estratificados. Cada mensagem é testada uma única vez,
  por um modelo que não a viu, e A, B e C usam os mesmos folds. Isso é melhor que um único teste de 12 mensagens.
- **Leave-one-source-out:** cada fonte real sai inteira do treino e da validação. Uma queda forte indica que o modelo
  dependia do estilo da fonte. *Limitação:* nas fontes de uma classe só (Externo 1, 4, 5 e 7), tirar a fonte também
  tira quase todos os exemplos reais daquela classe; a queda mistura "estilo" com "falta de dado".
- **Reais × sintéticos:** os sintéticos nunca vão para o teste. O efeito deles aparece em B × C no Facebook, mais um
  diagnóstico em que os modelos A e C, que nunca viram sintéticos, os classificam.

## 5. Critério de decisão (fixado antes dos resultados)

O modelo B só é exportado para o plugin se **todos** valerem:

1. F1 macro de B ≥ F1 macro de A + 0,03 no Facebook-CV;
2. F1 Seguro de B ≥ F1 Seguro de A, sem aumentar o alarme falso (Seguro→golpe) em mais de 0,05;
3. Acurácia de B no leave-Facebook-out ≥ a de A;
4. Nenhuma fonte com queda de acurácia > 0,15 de B em relação a A no leave-one-source-out;
5. F1 macro e F1 Seguro de B ≥ os do modelo atual do plugin nas mesmas 60 mensagens.

## 6. Resultados — modelo atual × modelo novo

Execução: Colab, Tesla T4, 16/11/2026, 2h20 no total; torch 2.4.0+cu121, transformers 4.44.2; base
`neuralmind/bert-base-portuguese-cased` na revisão `94d69c95`; determinismo completo. Os hashes de `pool_dedup.csv`
e `splits.json` conferem com os enviados. A tabela completa, com IC e matrizes, está em
`resultados_retreino/comparacao.md`; regenerei a comparação localmente e os números são idênticos.

### 6.1 Facebook-CV (60 mensagens, cada uma testada por um modelo que não a viu)

| Modelo | Acurácia | F1 macro [IC95%] | F1 Seguro [IC95%] | Recall / precisão Seguro | Alarme falso (Seguro→golpe) | Golpe perdido (golpe→Seguro) |
|---|---:|---|---|---|---:|---:|
| Atual no plugin ⚠ vazado | 0,617 | 0,619 | 0,500 | 0,50 / 0,50 | 0,50 | 0,08 |
| A — dados antigos | 0,400 | 0,399 [0,26–0,51] | 0,308 [0,00–0,62] | 0,25 / 0,40 | 0,75 | 0,06 |
| **B — unificado** | **0,550** | **0,532 [0,38–0,65]** | **0,435 [0,14–0,67]** | 0,62 / 0,33 | 0,38 | **0,19** |
| C — sem sintéticos | 0,450 | 0,469 [0,29–0,59] | 0,462 [0,18–0,67] | 0,75 / 0,33 | 0,25 | 0,23 |

F1 por classe:

| Modelo | Relac. | Financ. | Phish. | Loja F. | Desinf. | Seguro |
|---|---:|---:|---:|---:|---:|---:|
| Atual ⚠ vazado | 0,82 | 0,52 | 0,61 | 0,46 | 0,80 | 0,50 |
| A | 0,64 | 0,37 | 0,30 | 0,38 | 0,40 | 0,31 |
| **B** | **0,80** | **0,67** | 0,36 | 0,43 | 0,50 | 0,43 |
| C | 0,60 | 0,45 | 0,35 | 0,29 | 0,67 | 0,46 |

Matriz de confusão de B (linhas = verdadeiro; colunas = Relac., Financ., Phish., Loja F., Desinf., Seguro):

```
Relacionamento  8  0  0  0  0  2
Financeiro      1 11  0  0  0  1
Phishing        0  6  4  3  0  4
Loja Falsa      0  3  1  3  0  1
Desinformação   0  0  0  0  2  2
Seguro          1  0  0  0  2  5
```

Comparações pareadas, nas mesmas 60 mensagens:

| Comparação | Δ acurácia | Δ F1 macro [IC95%] | McNemar (só 1º / só 2º acertou) | p |
|---|---:|---|---:|---:|
| **B − A** | **+0,150** | **+0,134 [+0,03, +0,24]** | 11 / 2 | **0,022** |
| B − C (efeito dos sintéticos) | +0,100 | +0,063 [−0,02, +0,15] | 7 / 1 | 0,070 |
| C − A | +0,050 | +0,070 [−0,04, +0,18] | 7 / 4 | 0,549 |

**Como ler a linha do modelo atual.** Ele viu ~90% dessas mensagens no treino; o braço A é o mesmo tipo de modelo
(mesmos dados originais) medido honestamente, e cai para 0,40. Há também uma comparação justa com o plugin, porque
nenhum dos dois viu o **Telegram/Wpp** (96 mensagens). Nesse conjunto, B sem o Telegram no treino acerta **0,406**
contra **0,240** do plugin (22 contra 6 acertos exclusivos; McNemar p = 0,004). Porém, **nenhum dos dois reconhece
as 51 mensagens seguras do Telegram**: o plugin dá alarme em 90% delas e B em 100%. A vantagem de B ali vem só do
Financeiro.

### 6.2 Leave-one-source-out (a fonte inteira fora do treino e da validação)

| Fonte fora | n | Classes | Acurácia A | Acurácia B | Δ |
|---|---:|---|---:|---:|---:|
| **Interno (Facebook)** | 60 | todas | 0,40 | **0,53** | +0,13 |
| Externo 1 | 65 | Relac. | 0,00 | 0,09 | +0,09 |
| Externo 2 | 77 | Phish. + Seguro | 0,00 | 0,12 | +0,12 |
| Externo 3 | 104 | Desinf. + Seguro | 0,00 | 0,28 | +0,28 |
| Externo 4 | 35 | Financ. | 0,00 | 0,63 | +0,63 |
| Externo 5 | 25 | Financ. | 0,00 | 0,28 | +0,28 |
| Externo 6 | 43 | Loja F. + Seguro | 0,02 | 0,47 | +0,44 |
| Externo 7 | 36 | Loja F. | 0,00 | 0,11 | +0,11 |
| Telegram/Wpp | 96 | Financ. + Seguro | — | 0,41 | — |

- **Os dois braços aprenderam o estilo da fonte.** Com a validação (fontes vistas) em 0,52–0,82, as quedas para
  ~0 mostram que "classe" virou "jeito de escrever da fonte". Os zeros de A foram conferidos e não são bug. Exemplo:
  A sem o Externo 3 nunca prevê Seguro nem Desinformação. B sem o Externo 3 chama 93 de 104 notícias de "Seguro",
  inclusive as falsas: aprendeu "texto de notícia = seguro", sem distinguir notícia verdadeira de falsa.
- **B degrada menos em todas as fontes** (todos os Δ positivos). Os sintéticos, a única fonte balanceada, ajudam a
  desacoplar, mas nem de longe resolvem.
- Ressalva já prevista: nas fontes de uma classe só, sair a fonte também tira quase todo o dado real da classe.

### 6.3 Reais × sintéticos

- **Sintéticos no treino** (B × C, teste só com Facebook real): +0,10 de acurácia e +0,06 de F1 macro, não
  significativo (p = 0,07). O F1 Seguro fica parecido (0,43 contra 0,46). C dá menos alarme falso (0,25) e perde mais
  golpes (0,23). B é melhor em Relacionamento e Financeiro.
- **Diagnóstico** (não é teste): os modelos que nunca viram sintéticos acertam 56% deles (A) e 40% (C). Os
  sintéticos estão longe dos dados reais, sobretudo dos novos (Telegram); mesmo assim, pô-los no treino não piorou o
  Facebook.

### 6.4 Principais erros do modelo novo (B)

- **Phishing → Financeiro (6 de 17):** contas e links "para ganhar dinheiro" ("Clica no link da bio para ganhar
  💰", "CADE AS CONTAS PRA TRAMPO… ITAÚ, NEXT", "Compro Contas Pix CPF E CARTÃO"). A fronteira entre essas classes é
  tênue até para anotadores; vale revisar a definição.
- **Golpe → Seguro (10 de 52, contra 3 em A):** 4 Phishing, 2 Relacionamento ("42 anos, sem marido, sem
  filhos…"), 2 Desinformação ("A água de coco cura candidíase! #reels"). É o custo de o modelo ter aprendido a
  dizer "Seguro" com mais frequência: precisão Seguro de só 0,33.
- **Seguro → golpe (3 de 8):** um relato pessoal sobre quimioterapia vira Relacionamento; uma matéria do BBB e um
  post de pôr do sol com hashtags viram Desinformação. Hashtags e tom de notícia puxam para Desinformação.
- **Loja Falsa → Financeiro (3 de 8):** "VOLTO LIMITE DO SEU CARTÃO", "Compro Bradesco Net empresa", com
  confiança de até 0,84.
- Em 4 frases de teste que eu escrevi, o candidato final chamou de "Seguro" dois golpes óbvios ("vem ver meu vídeo
  👇 link" e "Ganhe R$500 por dia… chama no zap"). É só uma anedota, mas coerente com os 19% de golpe perdido.

### 6.5 Decisão

| Critério (fixado antes) | Resultado | Atendido |
|---|---|---|
| 1. F1 macro B ≥ A + 0,03 | 0,532 contra 0,399 | sim |
| 2. F1 Seguro B ≥ A, alarme falso sem subir > 0,05 | 0,435 contra 0,308; alarme 0,38 contra 0,75 | sim |
| 3. Leave-Facebook-out B ≥ A | 0,53 contra 0,40 | sim |
| 4. Nenhuma fonte com queda > 0,15 | todos os Δ positivos | sim |
| 5. B ≥ modelo atual do plugin (F1 macro e Seguro) | 0,532 / 0,435 contra 0,619 / 0,500 (vazado) | **não** |

**Recomendação: não substituir o modelo do plugin agora.** O critério 5 falha. Ele compara com um número inflado,
mas as medidas justas não salvam a classe que mais importa: no Telegram, B também erra 100% das mensagens seguras.
O F1 Seguro de B (0,43) está abaixo do 0,64 que se queria melhorar, e os golpes perdidos triplicaram. O ganho de B
sobre A é real e mostra que o caminho é dado, não arquitetura. O gargalo agora é a seção 7, itens 1 a 3.

Se mesmo assim vocês quiserem pôr B no plugin, por ser melhor que o atual em tudo o que foi medido de forma justa
(Telegram 0,41 contra 0,24; o braço A como proxy, 0,40 no Facebook), basta copiar `candidato/modelo_candidato/` para
`work/api_local/modelo_bert/`. Os rótulos e a arquitetura são idênticos, e já testei que ele carrega e roda com o
mesmo código do plugin (sha256 `a22df8a5…`). Façam isso com o alerta de que ele deixa passar mais golpes.

## 7. Recomendações de próximos passos

Os resultados confirmam o diagnóstico: o gargalo é o dado. Os itens 1 a 3 vêm primeiro.

1. **Aumentar o teste do Facebook antes de qualquer outra coisa.** Com 8 mensagens seguras, não dá para afirmar que
   o F1 Seguro passou de 0,64 para 0,70. Meta: pelo menos 50 por classe, coletadas e anotadas por duas pessoas
   (kappa ≥ 0,7), e nunca usadas no treino.
2. **Mensagens seguras com cara de Facebook.** Hoje são 8 de 161. Coletar comentários e posts comuns das mesmas
   páginas e grupos de onde vêm os golpes. Isso também desacopla fonte e classe.
3. **Negativos difíceis.** Avisos legítimos de banco, notícias reais sobre golpes, vendas reais no Marketplace,
   vagas reais. É exatamente onde o modelo atual erra: notícias legítimas viram "Desinformação".
4. **Trocar os traduzidos por nativos nas classes acopladas** (Relacionamento, Loja Falsa e Phishing são 75–89%
   traduzidas entre os reais). Usar FraudWhatsApp.Br, FraudTelegram.Br e alertas de Procon/Febraban.
5. **Diversificar a fonte das classes de fonte única** (Externo 1, 4, 5 e 7). O leave-one-source-out vai mostrar
   quais dependem do estilo.
6. **Calibrar a confiança.** Com a probabilidade máxima perto de 0,35, um limiar de alerta no plugin é quase
   aleatório. Aplicar temperature scaling na validação e expor "incerto" quando a confiança for baixa.
7. **Considerar uma pergunta binária primeiro** (golpe × seguro) antes do tipo de golpe. O erro que mais custa no uso
   real é o alarme falso em mensagem segura, e com 6 classes o sinal de "seguro" se dilui.
8. **Separar "notícia verdadeira" de "notícia falsa" com pares da mesma fonte.** O leave-one-source-out mostrou
   que o modelo trata qualquer texto em tom de notícia como uma classe só. Pares verdadeiro/falso sobre o mesmo
   assunto, como os que as agências de checagem publicam, forçam o modelo a olhar o conteúdo.
9. **Revisar a fronteira Phishing × Financeiro** no guia de anotação. "Compro contas Pix/CPF" e "link na bio para
   ganhar" aparecem nas duas classes, e é a confusão mais comum de B.
10. **Repetir este mesmo protocolo** (o notebook é retomável e determinístico) após cada rodada de coleta, com os
    mesmos cinco critérios.

## 8. Arquivos nesta entrega e como reproduzir

Os caminhos citados nas seções anteriores (`analise/`, `dados_retreino/`, `baseline/`, `resultados_retreino/`, `candidato/modelo_candidato/`) são da pasta de trabalho `retreino_dataset_unificado/`. Nesta entrega eles estão em `03_insumos/`, subpasta `retreino_dataset_unificado` de cada tipo:

| Onde | Conteúdo |
|---|---|
| `logs/retreino_dataset_unificado/` | `treinamento.log` (saída completa dos 33 treinos + teste rápido, Colab T4, 16/11), `status.json` (duração de cada etapa), logs de inferência da linha de base (`baseline_inferencia_plugin.log`, `…replicacao1.log`, `…replicacao2.log`) |
| `ambiente/retreino_dataset_unificado/` | `meta_execucao.json` (hiperparâmetros, hashes dos dados), `modelo_base.json` (revisão `94d69c95` do BERTimbau), `requirements-lock.txt`, `bootstrap_versoes.txt`, `gpu.txt` |
| `tabelas/retreino_dataset_unificado/` | análise (`analise_dataset.json`, `matriz_fonte_x_classe.csv`, `exemplos_quase_duplicatas.json`), `resumo_splits.json`, `baseline_resumo.json`, **`comparacao.md`/`.json`** (resultados da seção 6) |
| `amostras/retreino_dataset_unificado/` | `entrada/BrScamsFacebook_Unificado_2.xlsx` (dataset recebido), `dados/` (`pool_dedup.csv`, `dedup_removidos.csv`, `splits.json`), `baseline/` (predições do modelo do plugin e das replicações), `experimentos/<nome>/` (`predicoes.csv`, `predicoes_sinteticos_diag.csv`, `resultado.json` dos 33 experimentos) |
| `scripts/retreino_dataset_unificado/` | `analisar_dataset.py` → `preparar_splits.py` → `treinar_retreino.py` → `comparar.py`; `prever.py`, `resumo_baseline.py`, `criar_notebook.py` |
| `scripts/colab/Retreino_BERTimbau_Unificado_Colab_v3.ipynb` | notebook do Colab |
| `modelos/retreino_dataset_unificado/modelo_download.json` | **onde está o modelo B**: Hugging Face [`VitorMendonca62/veritaplugin-bert-retreino-unificado`](https://huggingface.co/VitorMendonca62/veritaplugin-bert-retreino-unificado) (público), revisão `d2db9dc4af7cc218a6f469b3423508b418e6ba44`, URL, tamanho e sha256 de cada arquivo. **Não instalado** (ver §6.5) |
| `scripts/baixar_modelo_hf.py` | `python3 -I 03_insumos/scripts/baixar_modelo_hf.py 03_insumos/modelos/retreino_dataset_unificado/modelo_download.json` baixa o modelo B nessa revisão e confere os hashes (só biblioteca padrão); para usar no plugin, copiar a pasta baixada para `work/api_local/modelo_bert/` |
| `modelos/retreino_dataset_unificado/modelo_candidato_metadados.json` | config e hashes do modelo B |

Não incluídos, por serem redundantes ou não necessários: `pacote_colab_retreino.zip` (as mesmas entradas acima), `dataset_anotado.csv` (gerado do xlsx por `analisar_dataset.py`) e `training_args.bin` do candidato (pickle com os argumentos do treino; não é necessário para carregar o modelo). Os pesos do candidato (436 MB) não estão na entrega: estão no Hugging Face (acima), com cópia local fora da entrega em `backup_pesos/retreino_dataset_unificado/modelo_candidato/`.

Para reproduzir: rodar o notebook no Colab com o pacote gerado por `criar_notebook.py`. A ordem dos scripts e os comandos, executados na pasta de trabalho, são:

```bash
cd retreino_dataset_unificado
../work/venv/bin/python -I scripts/analisar_dataset.py BrScamsFacebook_Unificado_2.xlsx analise
../work/venv/bin/python -I scripts/preparar_splits.py analise/dataset_anotado.csv dados_retreino <xlsx original de 450 linhas>
python3 -I scripts/criar_notebook.py        # gera o notebook e pacote_colab_retreino.zip
# treino: Colab. Depois de baixar resultados_retreino_metricas.zip:
../work/venv/bin/python -I scripts/comparar.py resultados_retreino dados_retreino resultados_retreino/comparacao.md resultados_retreino/comparacao.json
```
