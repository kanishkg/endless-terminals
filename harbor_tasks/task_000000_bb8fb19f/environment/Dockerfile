FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    sqlite3 \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install pytest

RUN mkdir -p /home/user/experiments && chmod 0777 /home/user && chmod 0777 /home/user/experiments

RUN sqlite3 /home/user/experiments/tracking.db "CREATE TABLE runs (id INTEGER PRIMARY KEY, experiment_name TEXT, started_at TEXT, ended_at TEXT, status TEXT, metrics_json TEXT);"

RUN sqlite3 /home/user/experiments/tracking.db " \
INSERT INTO runs (experiment_name, started_at, ended_at, status, metrics_json) VALUES \
('bert_finetune_v1', '2024-01-15 08:30:00', '2024-01-15 12:45:00', 'completed', '{\"accuracy\": 0.92, \"loss\": 0.08}'), \
('bert_finetune_v2', '2024-01-15 13:00:00', '2024-01-15 17:30:00', 'completed', '{\"accuracy\": 0.93, \"loss\": 0.07}'), \
('gpt2_baseline', '2024-01-16 09:00:00', '2024-01-16 15:00:00', 'completed', '{\"perplexity\": 25.4}'), \
('gpt2_finetuned', '2024-01-16 16:00:00', '2024-01-17 02:00:00', 'completed', '{\"perplexity\": 18.2}'), \
('resnet50_imagenet', '2024-01-17 08:00:00', '2024-01-17 20:00:00', 'completed', '{\"top1_acc\": 0.76, \"top5_acc\": 0.93}'), \
('resnet50_transfer', '2024-01-18 09:00:00', '2024-01-18 11:00:00', 'completed', '{\"accuracy\": 0.89}'), \
('vit_pretrain', '2024-01-18 12:00:00', '2024-01-19 12:00:00', 'completed', '{\"loss\": 0.15}'), \
('vit_finetune', '2024-01-19 14:00:00', '2024-01-19 18:00:00', 'completed', '{\"accuracy\": 0.91}'), \
('llama_eval', '2024-01-20 08:00:00', '2024-01-20 10:00:00', 'completed', '{\"bleu\": 0.42}'), \
('llama_finetune', '2024-01-20 11:00:00', '2024-01-21 11:00:00', 'failed', '{\"error\": \"OOM\"}'), \
('stable_diff_train', '2024-01-21 12:00:00', '2024-01-22 12:00:00', 'completed', '{\"fid\": 12.5}'), \
('stable_diff_v2', '2024-01-22 14:00:00', '2024-01-23 14:00:00', 'completed', '{\"fid\": 10.2}'), \
('whisper_finetune', '2024-01-23 16:00:00', '2024-01-23 22:00:00', 'completed', '{\"wer\": 0.08}'), \
('whisper_eval', '2024-01-24 08:00:00', '2024-01-24 09:00:00', 'completed', '{\"wer\": 0.09}'), \
('clip_train', '2024-01-24 10:00:00', '2024-01-25 10:00:00', 'completed', '{\"retrieval_acc\": 0.85}'), \
('clip_eval', '2024-01-25 11:00:00', '2024-01-25 12:00:00', 'completed', '{\"retrieval_acc\": 0.84}'), \
('t5_pretrain', '2024-01-25 13:00:00', '2024-01-27 13:00:00', 'completed', '{\"loss\": 0.12}'), \
('t5_finetune', '2024-01-27 14:00:00', '2024-01-27 20:00:00', 'completed', '{\"rouge\": 0.45}'), \
('roberta_mlm', '2024-01-28 08:00:00', '2024-01-28 16:00:00', 'completed', '{\"mlm_acc\": 0.72}'), \
('roberta_cls', '2024-01-28 17:00:00', '2024-01-28 21:00:00', 'completed', '{\"f1\": 0.88}'), \
('xlnet_train', '2024-01-29 08:00:00', '2024-01-30 08:00:00', 'failed', '{\"error\": \"NaN loss\"}'), \
('xlnet_debug', '2024-01-30 09:00:00', '2024-01-30 11:00:00', 'completed', '{\"loss\": 0.25}'), \
('albert_pretrain', '2024-01-30 12:00:00', '2024-01-31 00:00:00', 'completed', '{\"mlm_acc\": 0.68}'), \
('albert_finetune', '2024-01-31 01:00:00', '2024-01-31 05:00:00', 'completed', '{\"accuracy\": 0.87}'), \
('electra_train', '2024-01-31 06:00:00', '2024-01-31 18:00:00', 'completed', '{\"disc_acc\": 0.95}'), \
('electra_eval', '2024-01-31 19:00:00', '2024-01-31 20:00:00', 'completed', '{\"glue_avg\": 0.86}'), \
('deberta_v3', '2024-02-01 08:00:00', '2024-02-01 20:00:00', 'completed', '{\"accuracy\": 0.92}'), \
('deberta_squad', '2024-02-01 21:00:00', '2024-02-02 03:00:00', 'completed', '{\"em\": 0.85, \"f1\": 0.91}'), \
('longformer_pretrain', '2024-02-02 04:00:00', '2024-02-03 04:00:00', 'completed', '{\"loss\": 0.18}'), \
('longformer_qa', '2024-02-03 05:00:00', '2024-02-03 11:00:00', 'completed', '{\"f1\": 0.82}'), \
('bigbird_train', '2024-02-03 12:00:00', '2024-02-04 12:00:00', 'running', '{\"loss\": 0.22}'), \
('reformer_exp', '2024-02-04 13:00:00', '2024-02-04 19:00:00', 'completed', '{\"ppl\": 30.1}'), \
('performer_test', '2024-02-04 20:00:00', '2024-02-05 02:00:00', 'completed', '{\"ppl\": 28.5}'), \
('linformer_bench', '2024-02-05 03:00:00', '2024-02-05 09:00:00', 'completed', '{\"speed\": 1.5}'), \
('synthesizer_exp', '2024-02-05 10:00:00', '2024-02-05 16:00:00', 'failed', '{\"error\": \"config\"}'), \
('funnel_train', '2024-02-05 17:00:00', '2024-02-06 05:00:00', 'completed', '{\"accuracy\": 0.88}'), \
('mobilebert_dist', '2024-02-06 06:00:00', '2024-02-06 12:00:00', 'completed', '{\"speedup\": 4.2}'), \
('tinybert_train', '2024-02-06 13:00:00', '2024-02-06 17:00:00', 'completed', '{\"accuracy\": 0.84}'), \
('distilbert_exp', '2024-02-06 18:00:00', '2024-02-06 22:00:00', 'completed', '{\"accuracy\": 0.86}'), \
('squeezebert_v1', '2024-02-07 08:00:00', '2024-02-07 14:00:00', 'completed', '{\"latency_ms\": 15}'), \
('canine_pretrain', '2024-02-07 15:00:00', '2024-02-08 03:00:00', 'completed', '{\"char_acc\": 0.94}'), \
('byt5_train', '2024-02-08 04:00:00', '2024-02-09 04:00:00', 'completed', '{\"loss\": 0.14}'), \
('charbert_exp', '2024-02-09 05:00:00', '2024-02-09 11:00:00', 'completed', '{\"ner_f1\": 0.89}'), \
('mbart_translate', '2024-02-09 12:00:00', '2024-02-10 00:00:00', 'completed', '{\"bleu\": 0.38}'), \
('mt5_finetune', '2024-02-10 01:00:00', '2024-02-10 07:00:00', 'completed', '{\"rouge\": 0.41}'), \
('xlm_roberta_v2', '2024-02-10 08:00:00', '2024-02-10 16:00:00', 'completed', '{\"xnli_acc\": 0.81}'), \
('infoxlm_train', '2024-02-10 17:00:00', '2024-02-11 05:00:00', 'completed', '{\"retrieval\": 0.79}'); \
"

RUN chmod 0666 /home/user/experiments/tracking.db

WORKDIR /home/user

CMD ["/bin/bash"]
