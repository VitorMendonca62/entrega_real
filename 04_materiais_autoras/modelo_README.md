
# veritaplugin-bert

Classificador de **golpes digitais em português brasileiro**, obtido por *fine-tuning* do
[BERTimbau](https://huggingface.co/neuralmind/bert-base-portuguese-cased) sobre o dataset
[BrScamsFacebook](https://www.kaggle.com/datasets/brunaassisgt/brscamsfacebook). O modelo
classifica o texto de uma publicação do Facebook em uma de **6 categorias**, cinco delas
tipos de fraude e uma de conteúdo legítimo.

É o componente de classificação do **VeritaPlugin**, uma extensão de navegador que detecta
fraudes no Facebook e apresenta ao usuário a categoria do golpe, o enquadramento legal
aplicável e as ações recomendadas.

- **Artigo:** *VeritaPlugin: Uma Extensão de Navegador para Detecção Semântica de Fraudes no Facebook*
- **Código:** [github.com/brunanoroes/VeritaPlugin](https://github.com/brunanoroes/VeritaPlugin)
- **Treinamento:** [github.com/brunanoroes/treinamento-BERTimbau](https://github.com/brunanoroes/treinamento-BERTimbau)
- **Autora:** Bruna Norões — Universidade Federal Fluminense (UFF)

## Categorias

| id | Rótulo |
|---|---|
| 0 | Golpes Baseados Em Relacionamento |
| 1 | Golpes de Ganho Financeiro Ilusório |
| 2 | Ataques de Phishing e Roubo de Dados |
| 3 | Fraudes em Lojas Virtuais Falsas |
| 4 | Golpes de Desinformação Digital |
| 5 | Seguro |

## Como usar

```python
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

tok = AutoTokenizer.from_pretrained("brunanoroes/veritaplugin-bert")
mod = AutoModelForSequenceClassification.from_pretrained("brunanoroes/veritaplugin-bert")
mod.eval()

texto = "PARABÉNS! Você ganhou R$ 5.000. Clique no link e informe seus dados bancários."

e = tok(texto, return_tensors="pt", truncation=True, max_length=512)
with torch.no_grad():
    probs = torch.softmax(mod(**e).logits, dim=-1)[0]

i = int(probs.argmax())
print(mod.config.id2label[i], f"{probs[i]:.3f}")
# Golpes de Ganho Financeiro Ilusório 0.9xx
```

Com `pipeline`:

```python
from transformers import pipeline

clf = pipeline("text-classification", model="brunanoroes/veritaplugin-bert")
clf("Seu CPF foi bloqueado. Acesse o link e confirme seus dados em 24h.")
```

## Dados de treinamento

**BrScamsFacebook** — 450 instâncias rotuladas manualmente, **75 por categoria**
(perfeitamente balanceado). O dataset combina duas origens:

- **Coleta autoral no Facebook**, por meio de personas de observação, capturando posts,
  comentários e anúncios em condições autênticas de uso
- **Seis fontes externas**, entre elas o fórum ScamWarners, o SMS Spam Collection, uma base
  de fake news em português, o Fake Reviews Dataset e a base *sec-fraudimabr* (mensagens de
  WhatsApp e Telegram)

As fontes em inglês foram traduzidas automaticamente — ver *Limitações*.

### Divisão dos dados

A divisão aplica **estratificação dupla**, por categoria **e** por dataset de origem. Sem
isso, todos os exemplos de uma mesma fonte poderiam se concentrar em um único split,
levando o modelo a aprender o estilo de escrita de cada base em vez dos padrões reais dos
golpes.

| Conjunto | Proporção | Exemplos |
|---|---|---|
| Treino | 80% | 360 |
| Validação | 10% | 45 |
| Teste | 10% | 45 |

## Treinamento

Realizado no Google Colaboratory, em GPU NVIDIA Tesla T4 (16 GB de VRAM).

| Hiperparâmetro | Valor |
|---|---|
| Modelo base | `neuralmind/bert-base-portuguese-cased` |
| Learning rate | `2e-5` |
| Batch size | `16` |
| Épocas (máx.) | `4` |
| Weight decay | `0,01` |
| Optimizer | AdamW |
| Early stopping | paciência 2, sobre o F1-macro de validação |
| Max length | `512` tokens |
| Seed | `42` |

A variante `cased` do BERTimbau foi escolhida deliberadamente: ela preserva a distinção
entre maiúsculas e minúsculas, relevante em textos de redes sociais, onde grafias como
"URGENTE" carregam significado semântico.

## Avaliação

A métrica principal é a **validação cruzada estratificada com k = 5**, reportada como média
± desvio padrão. O holdout é apresentado como análise complementar: com apenas 7–8 exemplos
por categoria no conjunto de teste, uma única predição errada altera o F1 daquela categoria
em até 14 pontos percentuais, o que o torna instável como resultado principal.

### Validação cruzada (k = 5) — resultado principal

| Fold | F1-macro |
|---|---|
| 1 | 0,787 |
| 2 | 0,800 |
| 3 | 0,704 |
| 4 | 0,775 |
| 5 | 0,751 |
| **Média ± DP** | **0,763 ± 0,034** |

### Desempenho por categoria (consolidado, 450 avaliações)

| Categoria | Precisão | Recall | F1 |
|---|---|---|---|
| Golpes Baseados Em Relacionamento | 0,85 | 0,89 | **0,87** |
| Golpes de Ganho Financeiro Ilusório | 0,79 | 0,77 | 0,78 |
| Ataques de Phishing e Roubo de Dados | 0,82 | 0,75 | 0,78 |
| Golpes de Desinformação Digital | 0,77 | 0,80 | 0,78 |
| Fraudes em Lojas Virtuais Falsas | 0,75 | 0,68 | 0,71 |
| Seguro | 0,61 | 0,68 | **0,64** |

### Holdout 80/10/10

| Métrica | Valor |
|---|---|
| Acurácia | 82,2% |
| F1-macro | 0,828 |
| F1-weighted | 0,824 |

### Comparação com baselines

Ambos avaliados sob **protocolo e seed idênticos** (`StratifiedKFold(n_splits=5,
shuffle=True, random_state=42)`), o que torna os números diretamente comparáveis:

| Modelo | F1-macro |
|---|---|
| Classificador por maioria | 0,048 |
| TF-IDF + LinearSVC | 0,711 ± 0,027 |
| **BERTimbau fine-tuned (este modelo)** | **0,763 ± 0,034** |

O ganho sobre o baseline clássico é de **+0,052 de F1-macro**, e **não é uniforme**: ele se
concentra em *Desinformação Digital* (+0,15) e *Seguro* (+0,13) — as categorias que
dependem de compreensão contextual. Nas categorias marcadas por vocabulário característico
e recorrente (prêmios, dados bancários, ofertas), o TF-IDF alcança desempenho equivalente.

Os intervalos de ±1 desvio padrão dos dois modelos se sobrepõem marginalmente. Com k = 5 e
450 instâncias, a evidência favorece consistentemente o modelo neural, mas **não sustenta
superioridade categórica**: o TF-IDF + SVM é um baseline forte nesta tarefa.

## Usos pretendidos

**Uso pretendido:** triagem assistiva de conteúdo suspeito em redes sociais em português
brasileiro, em contexto de pesquisa acadêmica, sempre com um humano na decisão final.

**Fora do escopo:**

- Decisão automatizada sobre remoção de conteúdo, banimento de contas ou bloqueio de
  transações, sem revisão humana
- Determinação de culpa, de intenção criminosa ou de responsabilidade legal de qualquer
  pessoa
- Uso como prova em processo judicial ou administrativo
- Aplicação a idiomas diferentes do português brasileiro, ou a domínios distintos de redes
  sociais (e-mail corporativo, SMS bancário, etc.), sem reavaliação

## Limitações e riscos

**Dataset pequeno.** 450 instâncias, 75 por categoria. É um volume reduzido para
*fine-tuning* de um modelo BERT, e a variância entre folds (desvio padrão de 0,034)
reflete isso. Os resultados são indicativos e não devem ser extrapolados para populações
mais amplas de golpes.

**A categoria "Seguro" é a mais fraca (F1 = 0,64).** Este é o ponto de atenção prático mais
importante do modelo: ele **confunde conteúdo legítimo com golpe** com frequência
relativamente alta. Em uso real, isso significa falsos positivos — alertas sobre conteúdo
inofensivo — que podem gerar alarme desnecessário e, com o tempo, dessensibilizar o
usuário.

**Ruído de tradução automática.** Quatro das seis fontes externas foram traduzidas
automaticamente do inglês. Expressões idiomáticas de golpe traduzidas literalmente produzem
texto que nenhum golpista brasileiro escreveria, e o modelo pode ter aprendido, em parte,
padrões da tradução automática em vez de padrões reais de fraude em português.

**Validade temporal.** Golpes evoluem rapidamente em resposta às próprias defesas. O
dataset reflete um recorte temporal específico, e o desempenho tende a degradar com o
tempo, sobre golpes com formulações novas.

**Viés de plataforma e de coleta.** Os dados vêm majoritariamente do Facebook e de fóruns
de denúncia. Golpes que circulam em outras plataformas, ou que nunca são reportados, estão
sub-representados.

**Risco de uso indevido.** Um classificador de golpes pode, em princípio, ser usado
adversarialmente para testar formulações até encontrar as que escapam à detecção. A
publicação do modelo assume que o benefício defensivo, num cenário em que as vítimas hoje
não têm nenhuma proteção, supera esse risco.

**Não substitui orientação jurídica ou de segurança.** O modelo produz uma hipótese de
classificação, não um parecer.

## Considerações éticas

O dataset contém textos de golpes reais coletados de fontes públicas, podendo incluir
identificadores residuais de terceiros — inclusive de vítimas. O material foi disponibilizado
para fins exclusivos de pesquisa acadêmica e não deve ser usado para identificar ou contatar
indivíduos.

O sistema completo (VeritaPlugin) foi projetado para operar em conformidade com a **LGPD
(Lei nº 13.709/2018)**: o texto analisado é enviado sob demanda explícita do usuário, e
nenhuma chave, dado de navegação ou conteúdo é persistido em servidor.

## Licença

**MIT**, em consonância com a licença do modelo base
[BERTimbau](https://huggingface.co/neuralmind/bert-base-portuguese-cased) e com a dos
repositórios de código do projeto.

## Citação

```bibtex
@inproceedings{noroes2026veritaplugin,
  title     = {{VeritaPlugin}: Uma Extensão de Navegador para Detecção Semântica de Fraudes no Facebook},
  author    = {Norões, Bruna Assis},
  booktitle = {Simpósio Brasileiro de Segurança da Informação e de Sistemas Computacionais (SBSeg)},
  year      = {2026}
}
```

### Modelo base

```bibtex
@inproceedings{souza2020bertimbau,
  title     = {{BERTimbau}: Pretrained {BERT} Models for {B}razilian {P}ortuguese},
  author    = {Souza, F{\'a}bio and Nogueira, Rodrigo and Lotufo, Roberto},
  booktitle = {Brazilian Conference on Intelligent Systems (BRACIS)},
  year      = {2020}
}
```