# Linha de base TF-IDF no retreino com o dataset unificado — relatório

*24/11/2026 · execução: Google Colab (CPU, 2 núcleos), 01:30–01:35 UTC de 25/11 · dataset `BrScamsFacebook_Unificado_2.xlsx`
(sha256 `b5d89600…4014`, o mesmo do retreino) · semente 42 em tudo*

## 1. Resumo

**Fora da amostra, um modelo de palavras (TF-IDF) empata com o BERTimbau.** Nas mesmas 60 mensagens do Facebook,
com os mesmos 5 folds do retreino, o TF-IDF + LinearSVC das autoras acerta 33, e o BERTimbau do braço B também
acerta 33 (F1 macro 0,534 contra 0,532; McNemar p = 1,00). Nenhuma diferença entre os dois modelos é significativa
em nenhum dos três braços.

Isso reforça a conclusão do relatório de retreino: **o gargalo é o dado, não a arquitetura.** No artigo, o BERTimbau
superava o TF-IDF por 5 pontos de F1 macro num teste com as mesmas fontes do treino; num teste justo, a vantagem some.

| Achado | Evidência |
|---|---|
| TF-IDF ≈ BERTimbau no braço B | 33 × 33 acertos; ΔF1 macro +0,001 [−0,13, +0,13]; p = 1,00 |
| Mais dados ajudam o TF-IDF menos que o BERT | B − A no TF-IDF: +0,099 de F1 macro, p = 0,34. No BERT: +0,134, p = 0,022 |
| O TF-IDF também aprende o estilo da fonte | Leave-one-source-out: acurácia de 0,00 a 0,47 com a fonte fora |
| O script das autoras dá 0,711 no Colab | Igual ao README delas (0,711 ± 0,027); o artigo diz ≈0,67 |

## 2. Por que uma linha de base TF-IDF

O TF-IDF representa cada mensagem pelas palavras e pares de palavras que ela contém, com mais peso às raras;
o classificador (LinearSVC) aprende quais palavras indicam cada classe. Não tem compreensão de contexto, treina
em segundos e roda em CPU. Serve de régua: o BERTimbau só se justifica se for claramente melhor que ele.
As autoras fizeram essa comparação (seção de experimentos do artigo e repositório `Treinamento_TF-IDF-SVM`);
aqui ela é repetida com o protocolo de teste do retreino.

## 3. Protocolo

- **Modelo:** configuração das autoras, sem ajuste: `TfidfVectorizer(max_features=10000, ngram_range=(1,2),
  sublinear_tf=True)` + `LinearSVC(C=1.0, max_iter=2000, random_state=42)`. Também uma regressão logística
  (`class_weight="balanced"`) com o mesmo TF-IDF, que fornece probabilidades.
- **Dados:** mesma deduplicação do retreino (756 → 751; as mesmas 5 linhas removidas).
- **Facebook-CV:** as 60 mensagens do Facebook em 5 folds estratificados. **Os folds são idênticos aos do
  retreino** (conferido contra `splits.json` por `comparar_tfidf_bert.py`).
- **Braços:** A (445 originais), B (751 unificados), C (541 sem sintéticos), menos as 12 mensagens de teste do fold.
- **Diferença em relação ao BERT:** o BERT treina com `train` e escolhe a época em `val` (10% só de reais).
  O TF-IDF não tem época e treina com `train` + `val`. O teste é o mesmo.
- **Leave-one-source-out:** cada fonte real fica inteira fora do treino. Braços A e B.
- **Estatística:** McNemar exato e IC 95% bootstrap (10.000 reamostragens, semente 42) do ΔF1 macro.

## 4. Resultados

### 4.1 Facebook-CV (60 mensagens)

| Braço | Modelo | Acurácia | F1 macro | F1 Seguro | Alarme falso | Golpe perdido |
|---|---|---:|---:|---:|---:|---:|
| A | BERTimbau (retreino) | 0,400 | 0,399 | 0,308 | 0,75 | 0,06 |
| A | TF-IDF + SVM | 0,483 | 0,435 | 0,353 | 0,62 | 0,12 |
| A | TF-IDF + LR | 0,517 | 0,504 | 0,421 | 0,50 | 0,13 |
| B | BERTimbau (retreino) | 0,550 | 0,532 | 0,435 | 0,38 | 0,19 |
| B | TF-IDF + SVM | 0,550 | 0,534 | 0,500 | 0,38 | 0,13 |
| B | TF-IDF + LR | 0,550 | 0,535 | 0,455 | 0,38 | 0,17 |
| C | BERTimbau (retreino) | 0,450 | 0,469 | 0,462 | 0,25 | 0,23 |
| C | TF-IDF + SVM | 0,517 | 0,500 | 0,414 | 0,25 | 0,29 |
| C | TF-IDF + LR | 0,517 | 0,503 | 0,333 | 0,50 | 0,23 |

Linhas do BERTimbau: `tabelas/retreino_dataset_unificado/comparacao.md`. Linhas do TF-IDF:
`tabelas/tfidf_retreino/tabela_facebook_cv.csv`.

### 4.2 TF-IDF × BERTimbau, pareado (mesmas 60 mensagens)

| Braço | TF-IDF | Acertos TF-IDF / BERT | ΔF1 macro [IC 95%] | Só TF-IDF / só BERT acertou | McNemar p |
|---|---|---:|---|---:|---:|
| A | SVM | 29 / 24 | +0,036 [−0,12, +0,20] | 11 / 6 | 0,33 |
| A | LR | 31 / 24 | +0,106 [−0,01, +0,23] | 10 / 3 | 0,09 |
| B | SVM | 33 / 33 | +0,001 [−0,13, +0,13] | 6 / 6 | 1,00 |
| B | LR | 33 / 33 | +0,003 [−0,13, +0,14] | 6 / 6 | 1,00 |
| C | SVM | 31 / 27 | +0,031 [−0,11, +0,19] | 8 / 4 | 0,39 |
| C | LR | 31 / 27 | +0,034 [−0,08, +0,17] | 8 / 4 | 0,39 |

Fonte: `tabelas/tfidf_retreino/tfidf_vs_bert.csv`.

### 4.3 Entre braços, só TF-IDF + SVM

| Comparação | Δ acurácia | ΔF1 macro [IC 95%] | McNemar | p |
|---|---:|---|---:|---:|
| B − A | +0,067 | +0,099 [−0,02, +0,21] | 7 / 3 | 0,34 |
| C − A | +0,033 | +0,065 [−0,03, +0,17] | 5 / 3 | 0,73 |
| B − C | +0,033 | +0,034 [−0,04, +0,12] | 3 / 1 | 0,63 |

No BERTimbau, B − A foi significativo (p = 0,022). O TF-IDF também melhora com os dados novos, mas menos, e sem
significância com n = 60.

### 4.4 Leave-one-source-out (TF-IDF + SVM, acurácia)

| Fonte fora | n | A | B |
|---|---:|---:|---:|
| Interno (Facebook) | 60 | 0,35 | 0,47 |
| Externo 1 | 65 | 0,11 | 0,28 |
| Externo 2 | 77 | 0,04 | 0,13 |
| Externo 3 | 104 | 0,04 | 0,26 |
| Externo 4 | 35 | 0,17 | 0,37 |
| Externo 5 | 25 | 0,08 | 0,16 |
| Externo 6 | 43 | 0,12 | 0,21 |
| Externo 7 | 36 | 0,00 | 0,00 |
| Telegram/Wpp | 96 | 0,50 | 0,44 |

O TF-IDF degrada como o BERTimbau quando a fonte sai do treino: também associa classe a estilo de fonte.
No Telegram, 51 das 96 mensagens são seguras; um classificador que respondesse sempre "Seguro" acertaria 0,53,
mais que todos os modelos treinados. Por isso a acurácia no Telegram não deve ser lida sozinha.

## 5. Script original das autoras

`treinamento.py` do repositório `brunanoroes/Treinamento_TF-IDF-SVM`, commit `a6d2d0ae` (o mesmo da replicação de
20/10), rodado sem alteração no mesmo Colab: **F1 macro 0,711 ± 0,027**, idêntico ao README das autoras.

| Ambiente | scikit-learn / numpy / pandas | F1 macro |
|---|---|---:|
| Colab, 24/11/2026 | 1.6.1 / 2.4.6 / 2.2.3 | 0,711 ± 0,027 |
| Replicação, 20/10/2026 | 1.5.x | 0,703 ± 0,028 |
| Máquina da revisão, 24/11/2026 | 1.9.1 / 2.5.3 / 3.0.5 | 0,713 ± 0,026 |
| Artigo publicado | — | ≈0,67 |

Os folds são os mesmos nos três ambientes; mudam algumas predições (29 de 450 entre a replicação e a revisão).
A versão do scikit-learn sozinha não explica (1.5.2 a 1.9.1 deram 0,713 na mesma máquina). O valor do artigo
não se reproduz em nenhum ambiente testado.

Pelo mesmo motivo, o protocolo do retreino deu números um pouco diferentes fora do Colab (B e C variam 1 ou 2
acertos; A é idêntico). **Os números deste relatório são os do Colab.** Três execuções no Colab (21:47, 22:21 e
22:30 de 24/11) deram predições idênticas byte a byte (sha256 `d3f19de4…5d42`).

## 6. Limitações

- n = 60, com 8 mensagens seguras e 4 de Desinformação: os intervalos são largos e diferenças pequenas não são
  conclusivas. "Empata" é a leitura segura; "o TF-IDF é melhor" não é.
- O TF-IDF treina com 44 mensagens a mais por fold que o BERT (as da validação).
- Os sintéticos do braço B foram gerados tendo como referência 57 das 60 mensagens de teste (ver relatório de
  retreino). Isso afeta o TF-IDF e o BERT igualmente, então não muda a comparação entre eles.

## 7. Arquivos e como reproduzir

| Arquivo | Conteúdo |
|---|---|
| `scripts/tfidf_retreino/executar.py` | Roda os dois experimentos e organiza logs, ambiente, tabelas e amostras |
| `scripts/tfidf_retreino/rodar_tfidf.py` | Protocolo do retreino com TF-IDF |
| `scripts/tfidf_retreino/comparar_tfidf_bert.py` | Comparação pareada com as predições do BERTimbau |
| `logs/tfidf_retreino/` | `execucao.log` e `status.json` de cada experimento; `treinos.jsonl` (66 treinos) |
| `ambiente/tfidf_retreino/` | Proveniência (repositório e commit), hashes das entradas, sistema e `requirements-lock.txt` |
| `tabelas/tfidf_retreino/` | Métricas, tabelas por avaliação, matrizes de confusão, `tfidf_vs_bert.csv`, manifesto da execução |
| `amostras/tfidf_retreino/` | Predições por mensagem (scores das 6 classes), folds do Facebook, linhas removidas |

Os hashes de `executar.py` e `rodar_tfidf.py` nesta pasta são os registrados em
`ambiente/tfidf_retreino/entradas_sha256.json`: são exatamente os scripts que rodaram.

No Colab (CPU, ~4 min; precisa de acesso ao GitHub para clonar o repositório das autoras), a partir da raiz deste
repositório:

```bash
cd 03_insumos/scripts/tfidf_retreino
mkdir -p entrada && cp ../../amostras/retreino_dataset_unificado/entrada/BrScamsFacebook_Unificado_2.xlsx entrada/
python -I executar.py /content/execucao_colab
rm -r entrada            # a cópia do dataset não deve ser versionada aqui
```

Depois, a partir da raiz do repositório:

```bash
python -I 03_insumos/scripts/tfidf_retreino/comparar_tfidf_bert.py
```
