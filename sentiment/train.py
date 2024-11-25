# 필요한 라이브러리 임포트
import json
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, Trainer, TrainingArguments
from sklearn.model_selection import train_test_split

# 데이터 로드
with open('train.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 데이터 준비
texts = [item['content'] for item in data]
labels = [item['score'] for item in data]

# 레이블 매핑 (-1, 0, 1 -> 0, 1, 2)
label_mapping = {-1: 0, 0: 1, 1: 2}
labels = [label_mapping[label] for label in labels]

# 학습 데이터와 검증 데이터로 분할
train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.1, random_state=42
)

# 토크나이저와 모델 로드
tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")
model = AutoModelForSequenceClassification.from_pretrained("klue/roberta-base", num_labels=3)

# GPU 사용 설정
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 데이터 토크나이즈
train_encodings = tokenizer(train_texts, truncation=True, padding=True, max_length=512)
val_encodings = tokenizer(val_texts, truncation=True, padding=True, max_length=512)

# PyTorch 데이터셋 생성
class NewsDataset(torch.utils.data.Dataset):
    def __init__(self, encodings, labels):
        self.encodings = encodings
        self.labels = labels

    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        item['labels'] = torch.tensor(self.labels[idx])
        return item

    def __len__(self):
        return len(self.labels)

train_dataset = NewsDataset(train_encodings, train_labels)
val_dataset = NewsDataset(val_encodings, val_labels)

# 학습 인자 설정
training_args = TrainingArguments(
    output_dir='./results',          # 출력 디렉토리
    num_train_epochs=3,              # 에포크 수
    per_device_train_batch_size=8,   # 학습 배치 크기
    per_device_eval_batch_size=8,    # 평가 배치 크기
    eval_strategy='epoch',           # 평가 전략
    save_strategy='epoch',           # 모델 저장 전략
    learning_rate=2e-5,              # 학습률
    logging_dir='./logs',            # 로그 디렉토리
    logging_steps=100,
    load_best_model_at_end=True,     # 학습 종료 시 최고의 모델 로드
    fp16=True,                       # 혼합 정밀도 학습
)

# 트레이너 설정
trainer = Trainer(
    model=model,                         # 학습시킬 모델
    args=training_args,                  # 학습 인자
    train_dataset=train_dataset,         # 학습 데이터셋
    eval_dataset=val_dataset             # 평가 데이터셋
)

# 모델 학습
trainer.train()

# 모델 저장
trainer.save_model('./sentiment_model')
