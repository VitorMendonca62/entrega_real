# Resultados do retreino — comparação entre modelos

_Gerado por `scripts/comparar.py` a partir de `predicoes.csv` por exemplo. Todas as métricas do Facebook são **fora da amostra**: cada mensagem do Facebook só é testada por modelos que não a viram._

## 1. Facebook-CV (60 mensagens do Facebook, cada uma testada uma vez)

| Braço | n | Acurácia | F1 macro [IC95%] | F1 Seguro [IC95%] | Recall Seguro | Precisão Seguro | Alarme falso (Seguro→golpe) | Golpe perdido (golpe→Seguro) |
|---|---:|---:|---|---|---:|---:|---:|---:|
| A | 60 | 0.400 | 0.399 [0.26–0.51] | 0.308 [0.00–0.62] | 0.25 | 0.40 | 0.75 | 0.06 |
| B | 60 | 0.550 | 0.532 [0.38–0.65] | 0.435 [0.14–0.67] | 0.62 | 0.33 | 0.38 | 0.19 |
| C | 60 | 0.450 | 0.469 [0.29–0.59] | 0.462 [0.18–0.67] | 0.75 | 0.33 | 0.25 | 0.23 |

F1 por classe:

| Braço | Relacionamento | Financeiro | Phishing | Loja Falsa | Desinformação | Seguro |
|---|---:|---:|---:|---:|---:|---:|
| A | 0.64 | 0.37 | 0.30 | 0.38 | 0.40 | 0.31 |
| B | 0.80 | 0.67 | 0.36 | 0.43 | 0.50 | 0.43 |
| C | 0.60 | 0.45 | 0.35 | 0.29 | 0.67 | 0.46 |

Matriz de confusão (linhas = verdadeiro, colunas = previsto; ordem: Relacionamento, Financeiro, Phishing, Loja Falsa, Desinformação, Seguro):

**Braço A**

```
Relacionamento    7   0   0   0   1   2
Financeiro        1   5   4   2   0   1
Phishing          2   6   4   4   1   0
Loja Falsa        0   2   1   4   1   0
Desinformação     0   1   0   1   2   0
Seguro            2   0   1   2   1   2
```

**Braço B**

```
Relacionamento    8   0   0   0   0   2
Financeiro        1  11   0   0   0   1
Phishing          0   6   4   3   0   4
Loja Falsa        0   3   1   3   0   1
Desinformação     0   0   0   0   2   2
Seguro            1   0   0   0   2   5
```

**Braço C**

```
Relacionamento    6   0   0   0   0   4
Financeiro        1   7   1   2   0   2
Phishing          1   7   4   2   0   3
Loja Falsa        0   4   1   2   0   1
Desinformação     0   0   0   0   2   2
Seguro            2   0   0   0   0   6
```

### Comparações pareadas (mesmas 60 mensagens)

| Comparação | Δ acurácia | Δ F1 macro [IC95% bootstrap] | McNemar b/c | p exato |
|---|---:|---|---:|---:|
| B − A | +0.150 | +0.134 [+0.03, +0.24] | 11/2 | 0.022 |
| C − A | +0.050 | +0.070 [-0.04, +0.18] | 7/4 | 0.549 |
| B − C | +0.100 | +0.063 [-0.02, +0.15] | 7/1 | 0.070 |

_McNemar: b = acertou só o 1º modelo, c = acertou só o 2º. Com n=60 e 4–17 por classe, os intervalos são largos._

## 2. Modelo atual × modelo novo (mesmas 60 mensagens do Facebook)

O modelo atual e as duas replicações (treinados só com os 450 originais) viram ~90% destas mensagens no treino: os números deles estão **inflados por vazamento**. Mesmo assim é a referência do que o plugin faz hoje.

| Modelo | Fora da amostra? | Acurácia | F1 macro | F1 Seguro | Alarme falso (Seguro→golpe) | Golpe perdido (golpe→Seguro) |
|---|---|---:|---:|---:|---:|---:|
| **Atual — no plugin** (checkpoint publicado brunanoroes/veritaplugin-bert) | não (~90% vazado) | 0.617 | 0.619 | 0.500 | 0.50 | 0.08 |
| Replicação 1 (Colab 20/10) | não (~90% vazado) | 0.617 | 0.587 | 0.667 | 0.12 | 0.12 |
| Replicação 2 (Colab 26/10) | não (~90% vazado) | 0.617 | 0.612 | 0.632 | 0.25 | 0.10 |
| Retreino só com dados originais (A) | sim | 0.400 | 0.399 | 0.308 | 0.75 | 0.06 |
| **Novo — dataset unificado (B)** | sim | 0.550 | 0.532 | 0.435 | 0.38 | 0.19 |
| Unificado sem sintéticos (C) | sim | 0.450 | 0.469 | 0.462 | 0.25 | 0.23 |

_A comparação justa é A × B: mesmo código, mesmos folds, ambos fora da amostra. Se B supera o modelo atual mesmo com o atual favorecido pelo vazamento, o ganho real é ainda maior._

## 3. Leave-one-source-out (a fonte inteira fica fora do treino e da validação)

| Fonte (fora) | n | Acurácia A | Acurácia B | F1 macro* A | F1 macro* B | Δ acurácia (B−A) |
|---|---:|---:|---:|---:|---:|---:|
| Interno | 60 | 0.40 | 0.53 | 0.40 | 0.54 | +0.13 |
| Externo1 | 65 | 0.00 | 0.09 | 0.00 | 0.17 | +0.09 |
| Externo2 | 77 | 0.00 | 0.12 | 0.00 | 0.23 | +0.12 |
| Externo3 | 104 | 0.00 | 0.28 | 0.00 | 0.23 | +0.28 |
| Externo4 | 35 | 0.00 | 0.63 | 0.00 | 0.77 | +0.63 |
| Externo5 | 25 | 0.00 | 0.28 | 0.00 | 0.44 | +0.28 |
| Externo6 | 43 | 0.02 | 0.47 | 0.03 | 0.47 | +0.44 |
| Externo7 | 36 | 0.00 | 0.11 | 0.00 | 0.20 | +0.11 |
| Telegram-WppDataset | 96 | — | 0.41 | — | 0.38 | — |

*F1 macro só sobre as classes presentes na fonte (várias fontes têm 1 ou 2 classes: nelas a acurácia é o recall da classe). Telegram/Wpp não existe no braço A. Queda forte com a fonte fora = o modelo dependia do estilo da fonte.

## 4. Dados reais × sintéticos

- **Efeito de pôr os sintéticos no treino** (teste real = Facebook-CV): B (com) F1 macro 0.532, F1 Seguro 0.435; C (sem) F1 macro 0.469, F1 Seguro 0.462. Teste pareado B − C na seção 1.

**Diagnóstico (não é teste):** modelos que nunca viram sintéticos classificando os 210 sintéticos. Acerto alto = sintético parecido com o real; baixo = distribuição diferente.

| Braço | folds | Acurácia média | F1 macro | F1 Seguro |
|---|---:|---:|---:|---:|
| A | 5 | 0.559 | 0.525 | 0.328 |
| C | 5 | 0.398 | 0.364 | 0.333 |

_Regra do protocolo: sintéticos nunca entram no teste; por isso não existe "acurácia em sintéticos" do modelo B._

## 5. Principais erros do braço B no Facebook-CV

Confusões mais frequentes (verdadeiro → previsto):

- Phishing → Financeiro: 6
- Phishing → Seguro: 4
- Loja Falsa → Financeiro: 3
- Phishing → Loja Falsa: 3
- Desinformação → Seguro: 2
- Relacionamento → Seguro: 2
- Seguro → Desinformação: 2
- Financeiro → Relacionamento: 1

Erros de maior confiança (o modelo errou com convicção):

| linha xlsx | verdadeiro → previsto | conf. | texto |
|---:|---|---:|---|
| 10 | Loja Falsa → Financeiro | 0.84 | VOLTO LIMITE DO SEU CARTÃO DE CRÉDITO* 🟨 ITAU ✴️ 🟥 SANTANDER ♨️ *❌NAO PODE ESTÁ DEVENDO MAIS DE 3 MESES ❌*🆘pag |
| 280 | Phishing → Financeiro | 0.79 | Clica no link da bio para ganhar 💰 . . . . . . . . . . . . #leidaatração #atrairprosperidade #dinheiro #vida |
| 274 | Phishing → Financeiro | 0.79 | CADE AS CONTAS PRA TRAMPO [hidden information] chama     Pega ATÈ 50% doque VIRAR na conta    ITAÚ, NEXT, BRAD |
| 285 | Phishing → Financeiro | 0.73 | Mercado Pago que já vendeu no link, vem fazer dinheiro R$1.500 ou mais te ajudaria hoje? Se você já vendeu por |
| 20 | Financeiro → Relacionamento | 0.70 | 2026 - Prepare-se para viver a melhor experiência de lazer online! 🚀🎯 💥 Ganhe vantagens exclusivas e aproveite |
| 150 | Relacionamento → Seguro | 0.69 | 42 anos, sem marido, sem filhos e até eu mesma compro bolos 😢 |
| 11 | Loja Falsa → Financeiro | 0.67 | Compro Bradesco Net empresa aprovado hoje pago bem chama 🤑🤑 $750 pago indicação tbm 100 reais  Compro Next pag |
| 281 | Phishing → Financeiro | 0.66 | VOCÊ CONSEGUE 🚀 Já pensou em ganhar dinheiro no conforto da sua casa, perto da sua família com o seu celular?  |
| 448 | Seguro → Relacionamento | 0.56 | "Depois de 53 sessões de quimioterapia, de dias em que eu não tinha forças nem para levantar a cabeça e de noi |
| 271 | Phishing → Financeiro | 0.55 | Compro Contas Pix CPF , E CARTÃO! PIX CPF E CARTÃO  PIX CPF E CARTÃO PIX CPF E CARTÃO PIX CPF E CARTÃO # |
| 16 | Desinformação → Seguro | 0.54 | Sim, meninas. A água de coco cura candidíase!  #explore #reels #viral #dicas #beleza #candidiase #dicasdebelez |
| 272 | Phishing → Loja Falsa | 0.53 | Caso tenha interesse vou precisar desses dados abaixo para anexar no sistema ok?  FOTO DO RG:  CPF/ CNPJ:  EMA |

Mensagens seguras do Facebook classificadas como golpe:

- linha 448.0 → Relacionamento (conf. 0.56): "Depois de 53 sessões de quimioterapia, de dias em que eu não tinha forças nem para levantar a cabeça e de noi
- linha 94.0 → Desinformação (conf. 0.39): Confira aqui:  Quem está com mais votos para sair do 'BBB 26'? Veja como está votação entre Babu, Sarah e Sol
- linha 81.0 → Desinformação (conf. 0.33): Por do Sol, Orla de São Pedro da Aldeia, região dos Lagos, Rio de Janeiro. #creatorsearchinsights #sunset #por

## 6. Critério de decisão (definido antes de ver os resultados)

O modelo B só é recomendado para exportação se **todos** valerem:

1. F1 macro de B ≥ F1 macro de A + 0,03 no Facebook-CV;
2. F1 do Seguro de B ≥ F1 do Seguro de A, sem aumentar o alarme falso (Seguro→golpe) em mais de 0,05;
3. Acurácia de B no leave-Interno-out ≥ a de A;
4. Nenhuma fonte com queda de acurácia > 0,15 em B frente a A no leave-one-source-out;
5. F1 macro e F1 do Seguro de B ≥ os do modelo atual do plugin nas mesmas 60 mensagens (mesmo com o vazamento a favor do atual).

| Critério | Atendido |
|---|---|
| 1 | sim |
| 2 | sim |
| 3 | sim |
| 4 | sim |
| 5 | não |