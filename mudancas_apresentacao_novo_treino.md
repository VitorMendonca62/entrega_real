# Mudanças na apresentação `VeritaPlugin.pptx` com o novo treino do BERTimbau

**Base:** `execucao_20261026T164112242756Z.zip` (2ª execução, 26/10/2026) comparada à 1ª execução (20/10/2026) e aos resultados das autoras.
**Escopo:** o que alterar nos 20 slides. O deck não tem notas do apresentador. Os slides 10, 11 e 12 são imagens e não foram inspecionados.

## 1. O que mudou nos números

| Métrica | Autoras | 1ª execução (20/10) | 2ª execução (26/10) |
|---|---:|---:|---:|
| K-fold F1-macro | 0,7633 ± 0,0337 | 0,7656 ± 0,0364 | 0,7656 ± 0,0364 |
| Seguro (F1, K-fold) | 0,642 | 0,642 | 0,642 |
| Holdout F1-macro | 0,828 | 0,688 | **0,830** |
| Holdout acertos | 37/45 | 31/45 | **37/45** |
| Holdout acurácia | 0,8222 | 0,6889 | 0,8222 |

- O K-fold ficou idêntico nas duas execuções (os 5 folds coincidem ao quarto decimal). Nada muda na nota principal nem na vantagem sobre o método clássico.
- Só o **holdout** mudou. Com o mesmo código, os mesmos dados (hashes SHA-256 iguais) e a mesma seed, a 2ª execução reproduziu o resultado das autoras (37/45). A 1ª tinha dado 31/45.
- Isso é a **primeira evidência direta** de que o holdout varia entre execuções. Antes era só uma hipótese.
- F1 por categoria no holdout (autoras → 1ª → 2ª):
  - Relacionamento: 0,857 → 0,857 → 0,857
  - Financeiro: 0,923 → 0,923 → 0,923
  - Phishing: 0,706 → 0,667 → 0,750
  - Loja Falsa: 0,857 → 0,545 → 0,857
  - Desinformação: 0,875 → 0,737 → 0,857
  - Seguro: 0,750 → 0,400 → 0,737

## 2. Alterações por slide

### Slide 15: Replicação (obrigatória)
- **Atual:** "Treinamos o BERTimbau 6 vezes no Google Colab…"
- **Problema:** agora são duas execuções completas.
- **Sugestão:** "Treinamos o BERTimbau em **duas execuções completas** no Google Colab (cada uma com 5 folds e o holdout, 12 treinos no total), com a mesma GPU do artigo e o script original."

### Slide 16: Comparação (principal mudança)
É o único slide com números que mudam. Proposta:

1. **Coluna "Réplica", linha "Teste extra, com o nosso treino":**
   - Atual: `0,69`.
   - Novo: mostrar as duas execuções, **`0,69` (1ª) e `0,83` (2ª)**. Ou trocar por "0,69 a 0,83".
   - Não deixar só o 0,83 e não deixar só o 0,69: escolher um dos dois seria cherry-picking.
2. **Coluna "Réplica", linha "Nota principal":** está `0,763`, igual ao artigo. O valor medido é **0,766** (arredonda para 0,77). Corrigir para `0,766`, ou deixar `0,76` com nota, se a intenção for mostrar a equivalência.
3. **Primeira frase do texto lateral:**
   - Atual: "nosso modelo acertou 31 das 45 mensagens; o delas, 37."
   - Novo: "Com o mesmo código e os mesmos dados, nosso treino acertou **31 de 45 na 1ª execução e 37 de 45 na 2ª**; o modelo das autoras acertou 37."
4. **Frase do McNemar: remover ou reescrever.**
   - Atual: "Um teste estatístico pareado (McNemar, p = 0,031) confirma que a diferença não foi aleatória."
   - Motivo 1: com a 2ª execução igualando as autoras (37/45), a frase deixa de fazer sentido, porque a diferença desapareceu.
   - Motivo 2: a frase também contradiz os relatórios da equipe, que dizem que o McNemar "não é possível" (sem predições por exemplo das autoras) e que o teste disponível é Fisher, p ≈ 0,22 (`validacao_treinamento_BERT.md`, `holdout_teste_estatistico.json`). Ver §4.
   - Substituir por: "Duas execuções idênticas deram 31/45 e 37/45: a variação entre execuções é do mesmo tamanho da diferença para as autoras. Com 45 mensagens, a diferença não é estatisticamente significativa."
5. **"A IA termina com pouca certeza nas respostas, então pequenas variações mudam o resultado."** Manter. Agora está apoiada em dados.
6. **"A origem exata da variação não foi provada."** Manter, e acrescentar que o K-fold foi idêntico nas duas execuções e só o holdout variou. Uma hipótese é que a variação esteja no primeiro treino do processo. Não está provada.
7. **"A vantagem menor (6 pontos, e não 9)…"**
   - Manter. A comparação é feita pelo K-fold (0,766 contra o método clássico de 0,703), que não mudou.
   - Se o título do slide ou a coluna sugerirem que o holdout confirma a vantagem, esclarecer que a vantagem se refere ao K-fold.

### Slide 19: Conclusão
- "O resultado do teste extra depende do treino." Manter. Agora está mais forte, e vale acrescentar: "(mesmo código, duas execuções: 0,69 e 0,83)".
- "No Facebook, a classificação funciona: o resultado principal se confirmou." Continua correto, porque o K-fold é o resultado principal.

### Slides sem mudança
- Slides 1 a 14 e 17 a 20 não citam números afetados.
- Slide 14 reporta o artigo (0,763; 0,83; 0,87; 0,64).
- Slide 17 (Instagram) usa o modelo publicado das autoras, não o treino da equipe.
- Slide 18 (Possibilidades) não é afetado.

## 3. Texto sugerido para o slide 16 (pronto para colar)

| | Artigo | Réplica |
|---|---:|---:|
| Nota principal (F1, K-fold) | 0,763 | 0,766 |
| Mensagem segura (F1) | 0,64 | 0,64 |
| Teste extra, nosso treino | 0,83 | 0,69 (1ª) / 0,83 (2ª) |
| Teste extra, modelo das autoras | 0,83 | 0,83 |
| Vantagem sobre o método clássico | 9 pontos | 6 pontos |

Texto lateral:
- Com o mesmo código e os mesmos dados, nosso treino acertou 31 de 45 mensagens na 1ª execução e 37 de 45 na 2ª. O modelo das autoras acertou 37.
- A diferença entre nossas duas execuções é do tamanho da diferença para as autoras: o teste extra varia de uma execução para outra.
- O teste tem só 45 mensagens, então cada erro pesa mais de 2 pontos.
- Por isso a nota confiável é a da validação cruzada (0,766), que foi idêntica nas duas execuções.
- A origem exata da variação não foi provada.
- A vantagem menor (6 pontos, e não 9) vem do método clássico: as próprias autoras publicam dois números diferentes para ele.

## 4. Inconsistência a resolver antes de apresentar
O slide 16 cita McNemar (p = 0,031), mas `validacao_treinamento_BERT.md` e `holdout_teste_estatistico.json` dizem que o teste pareado não é possível e usam Fisher (p ≈ 0,22). Os dois não podem estar certos.
- p = 0,031 corresponde a 6 discordâncias, todas no mesmo sentido (2 × 0,5⁶). Isso é compatível com 31 contra 37 se as predições do checkpoint publicado das autoras existirem no repositório de vocês.
- Se esse cálculo não está documentado, a frase não deve ir para o slide.
- Com a 2ª execução igualando as autoras, a frase fica obsoleta de qualquer jeito.

## 5. Outros arquivos que precisam do mesmo ajuste
- `LEIA-ME.md`: a tabela de resultados traz "holdout 0,688 / 31/45 contra 37/45 / Fisher p ≈ 0,22".
- `02_relatorios/relatorio_replicacao.md` (cerca da linha 192), `validacao_treinamento_BERT.md`, `matriz_replicacao.csv` e `comparacao.csv`.
- O parágrafo do relatório que afirma que "fold 2 e holdout divergem" e levanta a hipótese de rodada diferente. A 2ª execução reproduz o holdout, o que enfraquece essa hipótese.
- Resultados de `extensao_integrada_bert_colab`: foram gerados com o modelo da 1ª execução. Indicar essa origem ou refazer com o modelo novo, se forem citados.
- Se a pasta `03_insumos/modelos` for atualizada, trocar o modelo, ou guardar os dois com a execução identificada.

## 6. Ressalvas
- Todos os números vêm dos JSONs e logs dos zips. Nenhum modelo foi rodado novamente: os "37/45" são a acurácia de 0,8222 aplicada a 45 exemplos.
- Não verifiquei se as predições exemplo a exemplo da 2ª execução coincidem com as das autoras. Só os agregados batem.
- A 2ª execução usou três bibliotecas auxiliares com versão diferente (`certifi`, `multidict`, `python-dateutil`). Isso não explica a variação do holdout, mas deve constar na reprodutibilidade.
