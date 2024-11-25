import os
import json
import tiktoken
from dotenv import load_dotenv
from openai import OpenAI

# .env 파일에서 API 키 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# GPT-4o-mini 모델의 최대 토큰 설정
MAX_TOKENS = 4096
MAX_RESPONSE_TOKENS = 50
MAX_PROMPT_TOKENS = MAX_TOKENS - MAX_RESPONSE_TOKENS

# 토큰 계산을 위한 tiktoken 인코더 로드
encoding = tiktoken.encoding_for_model("gpt-4o-mini")

# article.json 파일 읽기
try:
    with open('../article.json', 'r', encoding='utf-8') as f:
        articles = json.load(f)
    print(f"총 {len(articles)}개의 기사를 로드했습니다.")
except FileNotFoundError:
    print("article.json 파일을 찾을 수 없습니다.")
    exit()

train_data = []

# 감성 분석 수행
for idx, article in enumerate(articles, start=1):
    print(f"[{idx}/{len(articles)}] 기사 분석 중...")

    # 기사 내용 추출 및 결합
    content_list = article.get('content', [])
    content_text = ' '.join([item.get('text', '') for item in content_list])
    
    # 프롬프트 설정
    system_prompt = '''Forget all your previous instructions. Pretend you are a financial expert. You are a financial expert with stock recommendation experience. 
Respond with "1" for positive, "0" for neutral, and "-1" for negative. 
Provide only the score as your response.'''

    # 메시지 구성
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": content_text}
    ]

    # 토큰 계산
    def count_tokens(messages, encoding):
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # 메시지당 추가 토큰
            num_tokens += len(encoding.encode(message['content']))
        num_tokens += 2  # 보정치
        return num_tokens

    total_tokens = count_tokens(messages, encoding)
    print(f"  - 총 토큰 수: {total_tokens} (최대 {MAX_PROMPT_TOKENS} 허용)")

    # 토큰 초과 시 기사 내용을 줄임
    if total_tokens > MAX_PROMPT_TOKENS:
        print(f"  - 토큰 초과로 내용 줄이기...")
        available_tokens = MAX_PROMPT_TOKENS - count_tokens([messages[0]], encoding)
        encoded_content = encoding.encode(content_text)
        truncated_content = encoding.decode(encoded_content[:available_tokens])
        messages[1]['content'] = truncated_content
        print(f"  - 내용 줄임 완료.")

    # OpenAI API를 통해 감성 분석 요청
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=MAX_RESPONSE_TOKENS,
            n=1,
            temperature=0
        )
        print(f"  - OpenAI 응답 성공.")
    except Exception as e:
        print(f"  - OpenAI API 오류: {e}")
        continue

    # 응답 처리
    reply = response.choices[0].message.content.strip()
    try:
        score = int(reply)  # 응답을 정수로 변환
        if score not in [1, 0, -1]:
            raise ValueError("Unexpected score")
    except ValueError:
        print(f"  - 잘못된 응답: {reply}, 중립(0)으로 처리합니다.")
        score = 0

    # 결과 저장
    train_data.append({
        'content': content_text,
        'score': score
    })
    print(f"  - 감성 점수: {score}")

# 결과를 train.json 파일로 저장
output_file = 'train.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(train_data, f, ensure_ascii=False, indent=4)
print(f"결과를 '{output_file}'에 저장했습니다.")
