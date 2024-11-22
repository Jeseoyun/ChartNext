from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from hdfs import InsecureClient
import json
import time
import os
from datetime import datetime
from dotenv import load_dotenv
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler(f'streaming_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()

# 환경변수 설정
HDFS_URL = os.getenv('HDFS_URL')
HDFS_USER = os.getenv('HDFS_USER')
STREAMING_INTERVAL = int(os.getenv('STREAMING_INTERVAL', 300))
HDFS_DATA_PATH = os.getenv('HDFS_DATA_PATH', '/news_data/raw/articles.json')

# HDFS 클라이언트 설정
hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)

# 기존 데이터 로드
def load_existing_data():
    try:
        with hdfs_client.read(HDFS_DATA_PATH) as reader:
            return json.load(reader)
    except:
        return []

# URL 중복 체크를 위한 URL 집합 생성
def get_existing_urls():
    existing_data = load_existing_data()
    return {article['url'] for article in existing_data}

# 크롤링한 데이터 저장
def save_to_hdfs(new_articles):
    try:
        # 기존 데이터 로드
        existing_data = load_existing_data()
        
        # 새 데이터 추가
        all_data = existing_data + new_articles
        
        # 저장
        with hdfs_client.write(HDFS_DATA_PATH, encoding='utf-8') as writer:
            json.dump(all_data, writer, ensure_ascii=False, indent=4)
        logger.info(f"데이터 저장 완료: {HDFS_DATA_PATH} (기존: {len(existing_data)}개, 추가: {len(new_articles)}개, 총: {len(all_data)}개)")
    except Exception as e:
        logger.error(f"HDFS 저장 중 오류 발생: {str(e)}")
        # 로컬에 백업 저장
        backup_path = f'backup_stream_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(new_articles, f, ensure_ascii=False, indent=4)
        logger.info(f"백업 데이터 저장 완료: {backup_path}")

# ... (나머지 유틸리티 함수들은 mk_crawler.py와 동일)

def run_streaming():
    logger.info("스트리밍 크롤링 시작")
    
    while True:
        try:
            # 기존 URL 목록 가져오기
            existing_urls = get_existing_urls()
            new_articles = []  # 새로 크롤링한 기사 저장

            # 각 카테고리별로 최신 기사 크롤링
            for category, url in categories.items():
                logger.info(f"[{category}] 최신 기사 확인 중...")
                driver.get(url)
                
                # 첫 페이지의 기사만 확인
                news_nodes = get_fresh_nodes()
                
                for node in news_nodes:
                    try:
                        # 광고 및 많이 본 기사 건너뛰기 로직
                        # ... (mk_crawler.py와 동일)

                        # URL 중복 체크
                        article_url = link_element.get_attribute("href")
                        if article_url in existing_urls:
                            continue

                        # 기사 데이터 추출 및 저장 로직
                        # ... (mk_crawler.py와 동일)
                        
                        new_articles.append(article_data)
                        logger.info(f"[{category}] 새로운 기사 발견: {article_title}")

                    except Exception as e:
                        logger.error(f"[{category}] 기사 처리 중 오류: {str(e)}")
                        continue

            # 새로운 기사가 있으면 저장
            if new_articles:
                save_to_hdfs(new_articles)
                logger.info(f"새로운 기사 {len(new_articles)}개 저장 완료")
            else:
                logger.info("새로운 기사가 없습니다")

            # 다음 크롤링까지 대기
            logger.info(f"{STREAMING_INTERVAL}초 후 다음 크롤링 시작")
            time.sleep(STREAMING_INTERVAL)

        except Exception as e:
            logger.error(f"스트리밍 크롤링 중 오류 발생: {str(e)}")
            time.sleep(STREAMING_INTERVAL)  # 오류 발생 시에도 일정 시간 대기

if __name__ == "__main__":
    run_streaming() 