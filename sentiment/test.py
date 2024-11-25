from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch

# 모델 디렉토리 경로
model_dir = "./sentiment_model"

# 토크나이저와 모델 로드
tokenizer = AutoTokenizer.from_pretrained("klue/roberta-base")
model = AutoModelForSequenceClassification.from_pretrained(model_dir)

# 모델 평가 모드 전환 및 GPU 이동
model.eval()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

# 예측 함수
def predict_sentiment(text):
    # 텍스트 토크나이즈
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512).to(device)
    # 예측 수행
    with torch.no_grad():
        outputs = model(**inputs)
    logits = outputs.logits
    # 가장 높은 점수의 클래스 선택
    predicted_class = torch.argmax(logits, dim=1).item()
    # 레이블 매핑 (0, 1, 2 -> -1, 0, 1)
    label_mapping = {0: -1, 1: 0, 2: 1}
    return label_mapping[predicted_class]

# 테스트
text = "인공지능(AI) 시대 주식 투자금 절반은 미국 빅테크로 채우고 나머지는 글로벌 분산하세요."
predicted_label = predict_sentiment(text)
print(f"예측된 감성 점수: {predicted_label}")
