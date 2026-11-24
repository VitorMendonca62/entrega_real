"""
Treinamento e Avaliação — Fine-Tuning BERTimbau
================================================
Usa os arquivos gerados pelo preparar_dataset.py
Executa holdout + validação cruzada k=5
Gera todas as métricas e gráficos para o TCC
"""

import os
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use("Agg")

from sklearn.metrics import (
    classification_report, confusion_matrix,
    f1_score, accuracy_score
)

import subprocess, sys

def pip_install(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", pkg, "-q"])

try:
    import torch
except ImportError:
    pip_install("torch")
    import torch

try:
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback
    )
except ImportError:
    pip_install("transformers[torch]")
    from transformers import (
        AutoTokenizer, AutoModelForSequenceClassification,
        TrainingArguments, Trainer, EarlyStoppingCallback
    )

try:
    from datasets import load_dataset, Dataset as HFDataset
except ImportError:
    pip_install("datasets")
    from datasets import load_dataset, Dataset as HFDataset

# ── 1. CONFIGURAÇÕES ──────────────────────────────────────────────────────────

PASTA_DADOS = "dados_bert"
PASTA_SAIDA = "resultados_bert"
MODEL_NAME  = "neuralmind/bert-base-portuguese-cased"
RANDOM_SEED = 42
K_FOLDS     = 5
MAX_LENGTH  = 512

# ✅ Nomes exatos conforme aparecem na planilha
LABEL_MAP = {
    "Golpes Baseados Em Relacionamento":    0,
    "Golpes de Ganho Financeiro Ilusório":  1,
    "Ataques de Phishing e Roubo de Dados": 2,
    "Fraudes em Lojas Virtuais Falsas":     3,
    "Golpes de Desinformação Digital":      4,
    "Seguro":                               5,
}
ID2LABEL = {v: k for k, v in LABEL_MAP.items()}

NOMES_CURTOS = {
    0: "Relacionamento",
    1: "Financeiro",
    2: "Phishing",
    3: "Loja Falsa",
    4: "Desinformação",
    5: "Seguro",
}

TRAIN_ARGS = dict(
    num_train_epochs=4,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    learning_rate=2e-5,
    weight_decay=0.01,
    eval_strategy="epoch",
    save_strategy="epoch",
    load_best_model_at_end=True,
    metric_for_best_model="f1_macro",
    greater_is_better=True,
    logging_steps=10,
    seed=RANDOM_SEED,
    report_to="none",
)

os.makedirs(PASTA_SAIDA, exist_ok=True)

# ── 2. TOKENIZADOR ────────────────────────────────────────────────────────────

print(f"\nCarregando tokenizador: {MODEL_NAME}")
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

def tokenizar(batch):
    return tokenizer(
        batch["text"],
        truncation=True,
        padding="max_length",
        max_length=MAX_LENGTH,
    )

def carregar_jsonl(caminho: str) -> HFDataset:
    ds = load_dataset("json", data_files=caminho, split="train")
    ds = ds.map(tokenizar, batched=True)
    ds = ds.rename_column("label", "labels")
    ds.set_format("torch", columns=["input_ids", "attention_mask", "token_type_ids", "labels"])
    return ds

def carregar_csv(caminho: str) -> HFDataset:
    df = pd.read_csv(caminho, encoding="utf-8-sig")
    ds = HFDataset.from_dict({
        "text":  df["Mensagem"].tolist(),
        "label": df["label"].tolist(),
    })
    ds = ds.map(tokenizar, batched=True)
    ds = ds.rename_column("label", "labels")
    ds.set_format("torch", columns=["input_ids", "attention_mask", "token_type_ids", "labels"])
    return ds

# ── 3. MÉTRICAS ───────────────────────────────────────────────────────────────

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    return {
        "f1_macro":    round(f1_score(labels, preds, average="macro",    zero_division=0), 4),
        "f1_weighted": round(f1_score(labels, preds, average="weighted", zero_division=0), 4),
        "accuracy":    round(accuracy_score(labels, preds), 4),
    }

def avaliar_completo(trainer, ds_teste, nome="holdout"):
    pred_out = trainer.predict(ds_teste)
    preds    = np.argmax(pred_out.predictions, axis=-1)
    labels   = pred_out.label_ids

    todas_labels = list(range(len(LABEL_MAP)))
    todos_nomes  = [NOMES_CURTOS[i] for i in todas_labels]

    report = classification_report(
        labels, preds,
        labels=todas_labels,
        target_names=todos_nomes,
        output_dict=True,
        zero_division=0
    )
    print(f"\n{'─'*60}")
    print(f"RESULTADOS — {nome.upper()}")
    print(f"{'─'*60}")
    print(classification_report(
        labels, preds,
        labels=todas_labels,
        target_names=todos_nomes,
        zero_division=0
    ))

    return {
        "preds":       preds,
        "labels":      labels,
        "report":      report,
        "f1_macro":    report["macro avg"]["f1-score"],
        "f1_weighted": report["weighted avg"]["f1-score"],
        "accuracy":    report["accuracy"],
    }

# ── 4. TREINAR ────────────────────────────────────────────────────────────────

def treinar(ds_treino, ds_val, output_dir: str):
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=len(LABEL_MAP),
        id2label=ID2LABEL,
        label2id=LABEL_MAP,
    )
    args = TrainingArguments(output_dir=output_dir, **TRAIN_ARGS)
    trainer = Trainer(
        model=model,
        args=args,
        train_dataset=ds_treino,
        eval_dataset=ds_val,
        compute_metrics=compute_metrics,
        callbacks=[EarlyStoppingCallback(early_stopping_patience=2)],
    )
    trainer.train()
    # libera memória dos checkpoints intermediários imediatamente
    import shutil
    for item in os.listdir(output_dir):
        item_path = os.path.join(output_dir, item)
        if os.path.isdir(item_path) and item.startswith("checkpoint"):
            shutil.rmtree(item_path, ignore_errors=True)
    return trainer

# ── 5. GRÁFICOS ───────────────────────────────────────────────────────────────

def plot_confusion_matrix(labels, preds, titulo: str, caminho: str):
    todas = list(range(len(LABEL_MAP)))
    cm    = confusion_matrix(labels, preds, labels=todas)
    nomes = [NOMES_CURTOS[i] for i in todas]

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(cm, cmap="Blues")
    plt.colorbar(im, ax=ax)
    ax.set_xticks(range(len(nomes)))
    ax.set_yticks(range(len(nomes)))
    ax.set_xticklabels(nomes, rotation=35, ha="right", fontsize=9)
    ax.set_yticklabels(nomes, fontsize=9)
    ax.set_xlabel("Predito", fontsize=11)
    ax.set_ylabel("Real",    fontsize=11)
    ax.set_title(titulo,     fontsize=12, fontweight="bold")

    for i in range(len(nomes)):
        for j in range(len(nomes)):
            cor = "white" if cm[i, j] > cm.max() / 2 else "black"
            ax.text(j, i, str(cm[i, j]), ha="center", va="center",
                    color=cor, fontsize=10, fontweight="bold")

    plt.tight_layout()
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"  Matriz de confusão salva: {caminho}")

def plot_f1_por_categoria(report: dict, titulo: str, caminho: str):
    nomes = [NOMES_CURTOS[i] for i in range(len(LABEL_MAP))]
    f1s   = [report[n]["f1-score"] for n in nomes]
    cores = ["#3B6D11" if v >= 0.80 else "#854F0B" if v >= 0.65 else "#A32D2D" for v in f1s]

    fig, ax = plt.subplots(figsize=(9, 4))
    bars = ax.barh(nomes, f1s, color=cores, edgecolor="white", height=0.6)
    ax.set_xlim(0, 1.05)
    ax.set_xlabel("F1-Score", fontsize=11)
    ax.set_title(titulo, fontsize=12, fontweight="bold")
    ax.axvline(x=0.80, color="gray", linestyle="--", linewidth=0.8, label="meta 0.80")
    ax.legend(fontsize=9)
    for bar, v in zip(bars, f1s):
        ax.text(v + 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.2f}", va="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"  Gráfico F1 por categoria salvo: {caminho}")

def plot_kfold_f1s(f1_scores: list, caminho: str):
    media  = np.mean(f1_scores)
    desvio = np.std(f1_scores)
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar([f"Fold {i+1}" for i in range(len(f1_scores))],
                  f1_scores, color="#534AB7", edgecolor="white", width=0.5)
    ax.axhline(media, color="#D85A30", linestyle="--", linewidth=1.5,
               label=f"Média = {media:.3f} ± {desvio:.3f}")
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("F1-macro", fontsize=11)
    ax.set_title("F1-macro por fold — Validação cruzada k=5", fontsize=12, fontweight="bold")
    ax.legend(fontsize=10)
    for bar, v in zip(bars, f1_scores):
        ax.text(bar.get_x() + bar.get_width() / 2, v + 0.01,
                f"{v:.3f}", ha="center", fontsize=10)
    plt.tight_layout()
    plt.savefig(caminho, dpi=150)
    plt.close()
    print(f"  Gráfico k-fold salvo: {caminho}")

def salvar_resultados(dados: dict, caminho: str):
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(f"  Resultados salvos: {caminho}")

# ── 6. HOLDOUT ────────────────────────────────────────────────────────────────

def rodar_holdout():
    print("\n" + "=" * 60)
    print("ETAPA 1 — HOLDOUT 80/10/10")
    print("=" * 60)

    pasta_hf = os.path.join(PASTA_DADOS, "huggingface")
    print("Carregando e tokenizando datasets...")
    ds_treino = carregar_jsonl(os.path.join(pasta_hf, "train.jsonl"))
    ds_val    = carregar_jsonl(os.path.join(pasta_hf, "validation.jsonl"))
    ds_teste  = carregar_jsonl(os.path.join(pasta_hf, "test.jsonl"))
    print(f"  treino={len(ds_treino)} · validação={len(ds_val)} · teste={len(ds_teste)}")

    output_dir = os.path.join(PASTA_SAIDA, "holdout_checkpoints")
    print("\nIniciando treinamento holdout...")
    trainer = treinar(ds_treino, ds_val, output_dir)

    print("\nAvaliando no conjunto de teste...")
    resultado = avaliar_completo(trainer, ds_teste, nome="holdout")

    modelo_dir = os.path.join(PASTA_SAIDA, "modelo_final")
    trainer.save_model(modelo_dir)
    tokenizer.save_pretrained(modelo_dir)
    print(f"\n  Modelo salvo em: {modelo_dir}")

    plot_confusion_matrix(
        resultado["labels"], resultado["preds"],
        "Matriz de Confusão — Holdout",
        os.path.join(PASTA_SAIDA, "holdout_matriz_confusao.png")
    )
    plot_f1_por_categoria(
        resultado["report"],
        "F1-Score por categoria — Holdout",
        os.path.join(PASTA_SAIDA, "holdout_f1_categorias.png")
    )
    salvar_resultados({
        "f1_macro":    resultado["f1_macro"],
        "f1_weighted": resultado["f1_weighted"],
        "accuracy":    resultado["accuracy"],
        "report":      resultado["report"],
    }, os.path.join(PASTA_SAIDA, "holdout_metricas.json"))

    return resultado

# ── 7. K-FOLD ─────────────────────────────────────────────────────────────────

def rodar_kfold():
    print("\n" + "=" * 60)
    print("ETAPA 2 — VALIDAÇÃO CRUZADA k=5")
    print("=" * 60)

    pasta_kfold = os.path.join(PASTA_DADOS, "kfold")
    f1_scores   = []
    all_preds   = []
    all_labels  = []

    for fold in range(1, K_FOLDS + 1):
        print(f"\n{'─'*40}")
        print(f"FOLD {fold} / {K_FOLDS}")
        print(f"{'─'*40}")

        pasta_fold = os.path.join(pasta_kfold, f"fold_{fold}")
        ds_treino  = carregar_csv(os.path.join(pasta_fold, "treino.csv"))
        ds_teste   = carregar_csv(os.path.join(pasta_fold, "teste.csv"))
        print(f"  treino={len(ds_treino)} · teste={len(ds_teste)}")

        output_dir = os.path.join(PASTA_SAIDA, f"kfold_fold{fold}_checkpoints")
        trainer    = treinar(ds_treino, ds_teste, output_dir)
        resultado  = avaliar_completo(trainer, ds_teste, nome=f"fold {fold}")

        f1_scores.append(resultado["f1_macro"])
        all_preds.extend(resultado["preds"].tolist())
        all_labels.extend(resultado["labels"].tolist())

        salvar_resultados({
            "fold":        fold,
            "f1_macro":    resultado["f1_macro"],
            "f1_weighted": resultado["f1_weighted"],
            "accuracy":    resultado["accuracy"],
        }, os.path.join(PASTA_SAIDA, f"kfold_fold{fold}_metricas.json"))

    media  = float(np.mean(f1_scores))
    desvio = float(np.std(f1_scores))

    todas_labels = list(range(len(LABEL_MAP)))
    todos_nomes  = [NOMES_CURTOS[i] for i in todas_labels]

    print(f"\n{'=' * 60}")
    print(f"RESULTADO FINAL K-FOLD")
    print(f"{'=' * 60}")
    print(f"  F1-macro por fold : {[round(v, 3) for v in f1_scores]}")
    print(f"  F1-macro médio    : {media:.3f} ± {desvio:.3f}")
    print(f"\nRelatório consolidado (todos os folds):")
    print(classification_report(
        all_labels, all_preds,
        labels=todas_labels,
        target_names=todos_nomes,
        zero_division=0
    ))

    plot_kfold_f1s(f1_scores, os.path.join(PASTA_SAIDA, "kfold_f1_por_fold.png"))
    plot_confusion_matrix(
        all_labels, all_preds,
        "Matriz de Confusão Consolidada — k=5 folds",
        os.path.join(PASTA_SAIDA, "kfold_matriz_confusao_consolidada.png")
    )

    report_consolidado = classification_report(
        all_labels, all_preds,
        labels=todas_labels,
        target_names=todos_nomes,
        output_dict=True,
        zero_division=0
    )
    plot_f1_por_categoria(
        report_consolidado,
        "F1-Score por categoria — k=5 folds consolidado",
        os.path.join(PASTA_SAIDA, "kfold_f1_categorias_consolidado.png")
    )
    salvar_resultados({
        "f1_por_fold":        [round(v, 4) for v in f1_scores],
        "f1_macro_media":     round(media, 4),
        "f1_macro_desvio":    round(desvio, 4),
        "report_consolidado": report_consolidado,
    }, os.path.join(PASTA_SAIDA, "kfold_resultado_final.json"))

    return media, desvio, f1_scores

# ── 8. MAIN ───────────────────────────────────────────────────────────────────

def main():
    print(f"PyTorch  : {torch.__version__}")
    print(f"CUDA GPU : {'SIM — ' + torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'NÃO (CPU)'}")
    print(f"Modelo   : {MODEL_NAME}")
    print(f"Saída    : {PASTA_SAIDA}/")

    holdout_resultado = rodar_holdout()
    media, desvio, f1_scores = rodar_kfold()

    print(f"""
{'=' * 60}
RESUMO FINAL
{'=' * 60}

Holdout (teste fixo):
  F1-macro    : {holdout_resultado['f1_macro']:.3f}
  F1-weighted : {holdout_resultado['f1_weighted']:.3f}
  Acurácia    : {holdout_resultado['accuracy']:.3f}

Validação cruzada k=5 (resultado principal):
  F1-macro    : {media:.3f} ± {desvio:.3f}
  Por fold    : {[round(v, 3) for v in f1_scores]}

  "O modelo BERTimbau fine-tuned obteve F1-macro de {media:.3f} ± {desvio:.3f}
   na validação cruzada estratificada com k=5 folds."
{'=' * 60}
""")

if __name__ == "__main__":
    main()
