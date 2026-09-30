# ml/train_muril.py
import os
import torch
import torch.nn as nn
import pandas as pd
import numpy as np
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification,
    Trainer,
    TrainingArguments,
    DataCollatorWithPadding,
    set_seed
)
from sklearn.metrics import accuracy_score, precision_recall_fscore_support
from sklearn.utils.class_weight import compute_class_weight

os.environ["HF_HOME"] = r"D:\Projects\kollamo-ai\.cache\huggingface"
os.environ["HF_TOKEN"] = "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"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

torch.set_num_threads(os.cpu_count() or 4)
set_seed(42)

MODEL_NAME = "google/muril-base-cased"
LABEL2ID = {"Positive": 0, "Negative": 1, "Neutral": 2}
ID2LABEL = {0: "Positive", 1: "Negative", 2: "Neutral"}

class ManglishDataset(torch.utils.data.Dataset):
    def __init__(self, texts, labels, tokenizer):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        item = self.tokenizer(
            self.texts[idx],
            truncation=True,
            max_length=64,
            padding=False
        )
        item["labels"] = self.labels[idx]
        return item

class WeightedLossTrainer(Trainer):
    def __init__(self, class_weights=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.class_weights = class_weights

    def compute_loss(self, model, inputs, return_outputs=False, num_items_in_batch=None):
        labels = inputs.pop("labels")
        outputs = model(**inputs)
        logits = outputs.logits
        if self.class_weights is not None:
            loss_fct = nn.CrossEntropyLoss(weight=self.class_weights.to(model.device))
        else:
            loss_fct = nn.CrossEntropyLoss()
        loss = loss_fct(logits.view(-1, self.model.config.num_labels), labels.view(-1))
        return (loss, outputs) if return_outputs else loss

def compute_metrics(eval_pred):
    logits, labels = eval_pred
    preds = np.argmax(logits, axis=-1)
    precision, recall, f1, _ = precision_recall_fscore_support(
        labels, preds, average="macro", zero_division=0
    )
    acc = accuracy_score(labels, preds)
    return {
        "accuracy": round(acc, 4),
        "macro_f1": round(f1, 4),
        "macro_precision": round(precision, 4),
        "macro_recall": round(recall, 4)
    }

def train():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, "data", "processed")
    output_dir = os.path.join(base_dir, "saved_model")
    checkpoints_dir = os.path.join(base_dir, "checkpoints")
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(checkpoints_dir, exist_ok=True)

    print("[*] Loading processed splits...")
    train_df = pd.read_parquet(os.path.join(data_dir, "train.parquet"))
    val_df = pd.read_parquet(os.path.join(data_dir, "validation.parquet"))

    print(f"[+] Loaded {len(train_df)} train, {len(val_df)} validation rows.")

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

    train_labels = [LABEL2ID[label] for label in train_df["label"]]
    val_labels = [LABEL2ID[label] for label in val_df["label"]]

    train_dataset = ManglishDataset(train_df["text"].tolist(), train_labels, tokenizer)
    val_dataset = ManglishDataset(val_df["text"].tolist(), val_labels, tokenizer)

    classes = np.unique(train_labels)
    weights = compute_class_weight(class_weight="balanced", classes=classes, y=train_labels)
    class_weights = torch.tensor(weights, dtype=torch.float)
    print(f"[+] Computed balanced class weights: {class_weights.tolist()}")

    print("[*] Loading MuRIL architecture...")
    model = AutoModelForSequenceClassification.from_pretrained(
        MODEL_NAME,
        num_labels=3,
        id2label=ID2LABEL,
        label2id=LABEL2ID
    )

    # Freeze embeddings and encoder layers 0-10
    print("[*] Freezing embeddings and layers 0-10...")
    for param in model.bert.embeddings.parameters():
        param.requires_grad = False

    for name, param in model.bert.encoder.named_parameters():
        if not any(f"layer.{i}." in name for i in [10, 11]):
            param.requires_grad = False

    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    total_params = sum(p.numel() for p in model.parameters())
    print(f"[+] Active trainable parameters: {trainable_params:,} / {total_params:,} ({trainable_params/total_params:.1%})")

    data_collator = DataCollatorWithPadding(tokenizer=tokenizer)

    training_args = TrainingArguments(
        output_dir=checkpoints_dir,
        eval_strategy="epoch",
        save_strategy="epoch",
        learning_rate=6e-5,
        per_device_train_batch_size=32,
        per_device_eval_batch_size=32,
        num_train_epochs=3,
        warmup_steps=40,
        weight_decay=0.01,
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        logging_steps=25,
        save_total_limit=1,
        report_to="none"
    )

    trainer = WeightedLossTrainer(
        class_weights=class_weights,
        model=model,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        processing_class=tokenizer,
        data_collator=data_collator,
        compute_metrics=compute_metrics
    )

    print("\n[*] Starting focused fine-tuning run...")
    trainer.train()

    print(f"\n[*] Exporting final calibrated model to: {output_dir}")
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    print("[SUCCESS] Calibrated model and tokenizer exported successfully!")

if __name__ == "__main__":
    train()