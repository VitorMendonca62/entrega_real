# Entrega real — Etapa 01: replicação do VeritaPlugin

**Artigo:** Norões, B. A.; Rocha, B. M. S.; Motta, R. *VeritaPlugin: Uma Extensão de Navegador para Detecção Semântica de Fraudes no Facebook*. SBSeg 2026. DOI [10.5753/sbseg.2026.26924](https://doi.org/10.5753/sbseg.2026.26924).
**Equipe:** Vitor Mendonça, Julia Nunes e Luis Felipe. **Execução:** 20/10/2026. **Apresentação:** 21/10 ou 26/10/2026, a confirmar.

Esta pasta reúne a apresentação, os relatórios e **todos os insumos obtidos durante a replicação**: logs, amostras, modelos, imagens, tabelas, scripts e ambiente. Os materiais das autoras ficam separados dos produzidos pela equipe. O índice completo, arquivo por arquivo e com a origem de cada um, está em [INDICE_INSUMOS.md](INDICE_INSUMOS.md).

## Estrutura

| Pasta | Conteúdo |
|---|---|
| `01_apresentacao/` | Slides `.pptx` (15 slides, notas, ~18 min), roteiro em Markdown e conteúdo estruturado |
| `02_relatorios/` | Relatório técnico revisado, matriz de replicação, tabela de comparação e relatórios por experimento |
| `03_insumos/logs/` | Logs de instalação, preparação, baseline, treinamento Colab, servidores e controle de gasto |
| `03_insumos/amostras/` | Splits regenerados, predições, 190 entradas/saídas GPT-4o (brutas e filtradas), prompts e páginas de teste |
| `03_insumos/modelos/` | **Modelo BERTimbau treinado pela equipe** (1ª execução, holdout, Colab T4, em `bert_colab_holdout/`; 2ª execução, 26/10, em `bert_colab_execucao2/`: config e tokenizer aqui, pesos no Hugging Face), metadados do checkpoint público das autoras e do modelo do retreino |
| `03_insumos/imagens/` | Gráficos derivados dos resultados e capturas de tela reais da extensão e da réplica |
| `03_insumos/tabelas/` | Métricas por fold e por classe, matrizes de confusão, auditorias, latências, custos e reanálises (CSV/JSON) |
| `03_insumos/scripts/` | Scripts do treinamento BERT, notebook Colab, patches e extensão adaptada para localhost |
| `03_insumos/ambiente/` | Versões, lockfiles, GPU, commits e proveniência |
| `04_materiais_autoras/` | PDF do artigo e snapshots dos seis repositórios das autoras (não produzidos pela equipe) |

Dentro de cada tipo, as subpastas indicam o experimento: `baseline_tfidf_svm`, `bert_treinamento_colab`, `bert_checkpoint_publicado`, `dados_splits_regenerados`, `dados_auditoria`, `rag_filtro_e_reanalise`, `gpt4o_piloto`, `gpt4o_v1_v2_v3`, `extensao_integrada_checkpoint_publicado`, `extensao_integrada_bert_colab`, `api_e_replica`, `reanalise_sus_juridico`, `comparacao` e `retreino_dataset_unificado`.

## Resultados principais

| Métrica | Artigo | Esta replicação | Leitura |
|---|---:|---:|---|
| Baseline TF-IDF+SVM, F1-macro CV | ≈0,67 | 0,703 ± 0,028 | +3,34 pp; o valor do artigo é arredondado e o README atual informa 0,711 |
| BERTimbau, F1-macro CV k=5 | 0,763 ± 0,034 | 0,766 ± 0,036 | 4 de 5 folds idênticos aos das autoras; o fold 2 difere em +1,14 pp |
| BERTimbau, F1-macro holdout | 0,828 | 0,688 | 31/45 contra 37/45; Fisher p ≈ 0,22 (n=45, sem significância) |
| Latência clique→modal | não quantificada | 2,3–4,7 s (n=12) | 80–90% do tempo (mediana) é a chamada ao GPT-4o |
| SUS / avaliação jurídica | trabalho futuro | 87,0 / 49 de 72 pertinentes | Reanálise dos dados das autoras, sem novos participantes |

Gráfico-resumo: `03_insumos/imagens/comparacao/artigo_vs_replicacao.png`.

## Retreino com o dataset unificado (16–17/11/2026)

O BERTimbau foi retreinado com o novo dataset `BrScamsFacebook_Unificado_2.xlsx` (756 mensagens, 751 após remover duplicatas), com o mesmo pipeline e 33 treinos no Colab (T4). O relatório completo está em [`02_relatorios/retreino_dataset_unificado.md`](02_relatorios/retreino_dataset_unificado.md); os insumos ficam na subpasta `retreino_dataset_unificado` de cada tipo em `03_insumos/` (logs, ambiente, tabelas, amostras, scripts e modelo), e o notebook em `03_insumos/scripts/colab/Retreino_BERTimbau_Unificado_Colab_v3.ipynb`.

- **O dataset novo melhora o modelo:** no Facebook, fora da amostra, acurácia 0,40 → 0,55 e F1 macro 0,40 → 0,53 (p = 0,02).
- **Não substituiu o modelo do plugin:** F1 Seguro 0,43, golpes perdidos 19%, e o modelo ainda aprende o estilo da fonte. O modelo candidato não foi instalado. Os pesos estão no Hugging Face ([`VitorMendonca62/veritaplugin-bert-retreino-unificado`](https://huggingface.co/VitorMendonca62/veritaplugin-bert-retreino-unificado), revisão `d2db9dc4`) e não nesta pasta; baixe e confira os hashes com `03_insumos/scripts/baixar_modelo_hf.py` (ver abaixo).
- **O gargalo é o dado:** poucas mensagens seguras do Facebook e classes acopladas às fontes.

### Linha de base TF-IDF no retreino (24/11/2026)

A configuração TF-IDF + LinearSVC das autoras foi rodada no Colab com o mesmo protocolo e os mesmos folds do retreino. Relatório: [`02_relatorios/tfidf_retreino.md`](02_relatorios/tfidf_retreino.md); insumos na subpasta `tfidf_retreino` de cada tipo em `03_insumos/`.

- **Fora da amostra, o TF-IDF empata com o BERTimbau:** no braço B, 33 contra 33 acertos nas 60 mensagens do Facebook (F1 macro 0,534 contra 0,532; McNemar p = 1,00). Nenhuma diferença entre os dois é significativa em nenhum braço.
- **O script original das autoras dá 0,711 ± 0,027 no Colab**, igual ao README delas; o artigo diz ≈0,67.

## Quem produziu o quê

- **Execução (20/10/2026):** ambiente, baseline, splits, auditorias, treinamento BERT no Colab, API local, extensão no Chromium, 190 chamadas GPT-4o (custo estimado em US$ 1,02, com teto de US$ 3), reanálises, relatórios e slides.
- **Revisão (20/10/2026):** conferência dos números contra os dados brutos; correções nos relatórios (ver §15 do relatório); tabelas e gráficos complementares; teste estatístico do holdout; comparação fold a fold; organização desta pasta; manifesto SHA-256; reexecução de verificação do baseline (predições idênticas byte a byte, ver `03_insumos/logs/revisao/`).
- **Autoras:** tudo em `04_materiais_autoras/`. Os snapshots incluem os diretórios `.git` originais. `git rev-parse HEAD` confirma, nos seis repositórios, os commits registrados em `proveniencia.json`; o LEIA-ME do pacote anterior dizia, incorretamente, que não havia `.git`. Os dois `training_args.bin` dos repositórios das autoras foram omitidos: são arquivos pickle que nunca foram carregados e não são necessários.

## Como reproduzir

Os scripts da execução usam caminhos relativos ao layout original (`evidencias/autores`, `evidencias/execucao`); a correspondência entre esse layout e esta pasta está em `03_insumos/tabelas/_controle/mapa_caminhos.csv`. Os comandos executados estão em `02_relatorios/complementares/comandos_e_limitacoes.md`. As dependências estão em `03_insumos/ambiente/ambiente_e_proveniencia/pacote_requirements-lock.txt`. O treinamento BERT usa o notebook `03_insumos/scripts/colab/Treinar_BERTimbau_VeritaPlugin_v3.ipynb` em GPU (T4: cerca de 20 min). As chamadas ao GPT-4o exigem uma chave própria e um teto de gasto: não reexecute sem autorização de orçamento.

**Pesos dos modelos da equipe:** para não pesar na entrega, os pesos (`model.safetensors`, 436 MB cada) estão no Hugging Face, em repositórios públicos com revisão fixa. O `modelo_download.json` de cada pasta registra repositório, revisão, URL e sha256 de cada arquivo. Para baixar e conferir os hashes (só biblioteca padrão; um hash diferente interrompe o script):

```bash
python3 -I 03_insumos/scripts/baixar_modelo_hf.py 03_insumos/modelos/bert_colab_holdout/modelo_download.json
python3 -I 03_insumos/scripts/baixar_modelo_hf.py 03_insumos/modelos/bert_colab_execucao2/modelo_download.json
python3 -I 03_insumos/scripts/baixar_modelo_hf.py 03_insumos/modelos/retreino_dataset_unificado/modelo_download.json
```

| Modelo | Hugging Face | Revisão |
|---|---|---|
| Replicação, 1ª execução (20/10) | [`VitorMendonca62/veritaplugin-bert-replicacao-holdout`](https://huggingface.co/VitorMendonca62/veritaplugin-bert-replicacao-holdout) | `e773157a` |
| Replicação, 2ª execução (26/10) | [`VitorMendonca62/veritaplugin-bert-replicacao-execucao2`](https://huggingface.co/VitorMendonca62/veritaplugin-bert-replicacao-execucao2) | `2252be93` |
| Retreino, modelo B (não instalado) | [`VitorMendonca62/veritaplugin-bert-retreino-unificado`](https://huggingface.co/VitorMendonca62/veritaplugin-bert-retreino-unificado) | `d2db9dc4` |

Os dois primeiros comandos recolocam os pesos em `03_insumos/modelos/bert_colab_holdout/` e `03_insumos/modelos/bert_colab_execucao2/`, que já têm config e tokenizer; o terceiro baixa o modelo do retreino para `03_insumos/modelos/retreino_dataset_unificado/modelo_candidato/`. Há uma cópia local dos pesos fora da entrega, em `../backup_pesos/`.

**Modelo das autoras:** `brunanoroes/veritaplugin-bert`, revisão `d05bc15ad4821dbf629ca9473fc30387299b44de` (ver `03_insumos/modelos/bert_checkpoint_publicado/modelo_download.json`). O checkpoint não foi copiado, porque é material das autoras e está disponível publicamente.

## Segurança

Nenhuma chave de API está nesta pasta: a chave usada fica em `work/api_local/.env`, fora da entrega. As amostras contêm textos e URLs reais de golpes; não abra links. Os exemplos citados nos relatórios usam linha e hash, sem dados pessoais.

## Pendências manuais

1. Confirmar a data da apresentação.
2. No `.pptx` e em `apresentacao_notas.md`, corrigir “Vitor Mendona” para “Vitor Mendonça”, se for o caso, e considerar incluir o teste estatístico do holdout e a comparação fold a fold (os slides não foram alterados).
3. Ensaiar com cronômetro: o roteiro prevê 18 min.
4. Se a chave usada no GPT-4o não for mais necessária, revogá-la no painel da OpenAI.
