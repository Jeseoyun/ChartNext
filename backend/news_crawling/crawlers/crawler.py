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
        logging.FileHandler(f'crawling_{datetime.now().strftime("%Y%m%d")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 환경변수 로드
load_dotenv()

# 환경변수 설정
HDFS_URL = os.getenv('HDFS_URL')
HDFS_USER = os.getenv('HDFS_USER')
ARTICLES_PER_CATEGORY = int(os.getenv('INITIAL_ARTICLES_PER_CATEGORY', 10000))
HDFS_DATA_PATH = os.getenv('HDFS_DATA_PATH', '/news_data/raw/articles.json')

# HDFS 클라이언트 설정
hdfs_client = InsecureClient(HDFS_URL, user=HDFS_USER)

# 기존 데이터 로드
def load_existing_data():
    try:
        with hdfs_client.read(HDFS_DATA_PATH, encoding='utf-8') as reader:
            return json.load(reader)
    except:
        return []

# 크롤링한 데이터 저장
def save_to_hdfs(articles_data):
    try:
        # 기존 데이터 로드
        existing_data = load_existing_data()

        # 새 데이터 추가
        all_data = existing_data + articles_data

        # 저장 (overwrite=True 옵션 추가)
        with hdfs_client.write(HDFS_DATA_PATH, overwrite=True, encoding='utf-8') as writer:
            json.dump(all_data, writer, ensure_ascii=False, indent=4)
        logger.info(f"데이터 저장 완료: {HDFS_DATA_PATH} (기존: {len(existing_data)}개, 추가: {len(articles_data)}개, 총: {len(all_data)}개)")
    except Exception as e:
        logger.error(f"HDFS 저장 중 오류 발생: {str(e)}")

# 크롬 드라이버 설정
options = Options()
# options.add_argument("--headless")  # 브라우저 창을 띄우지 않음
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

print("크롬 드라이버 초기화 중...")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
print("크롬 드라이버 초기화 완료")

# 카테고리별 URL
categories = {
    "economy": "https://www.mk.co.kr/news/economy/latest/",
    "business": "https://www.mk.co.kr/news/business/latest/",
    "society": "https://www.mk.co.kr/news/society/latest/",
    "world": "https://www.mk.co.kr/news/world/latest/",
    "stock": "https://www.mk.co.kr/news/stock/latest/",
    "politics": "https://www.mk.co.kr/news/politics/latest/",
    "it": "https://www.mk.co.kr/news/it/latest/",
    "culture": "https://www.mk.co.kr/news/culture/latest/",
}

# 중복 방지를 위한 기사 URL 저장소
processed_urls = set()

def get_fresh_nodes():
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "li.news_node")))
    return driver.find_elements(By.CSS_SELECTOR, "li.news_node")

def extract_content(driver):
    content_elements = driver.find_elements(By.CSS_SELECTOR, "div.news_cnt_detail_wrap p")
    if not any(element.text.strip() for element in content_elements):
        article_body = driver.find_element(By.CSS_SELECTOR, "div.news_cnt_detail_wrap")
        content_elements = [article_body]

    content_data = []
    for p_element in content_elements:
        text_content = p_element.text.strip()
        if text_content:
            content_data.append({
                "refid": p_element.get_attribute("refid"),
                "text": text_content
            })
    return content_data

# 메인 크롤링 로직
for category, url in categories.items():
    logger.info(f"\n[{category}] 크롤링 시작... (목표: {ARTICLES_PER_CATEGORY}개)")
    driver.get(url)
    articles_crawled = 0

    while articles_crawled < ARTICLES_PER_CATEGORY:
        try:
            logger.info(f"[{category}] 기사 목록 로딩 중...")
            news_nodes = get_fresh_nodes()
            current_nodes_count = len(news_nodes)
            logger.info(f"[{category}] {current_nodes_count}개의 기사 발견")

            # 새로운 기사 발견 여부를 추적하는 변수
            new_articles_found = False

            # 기사 리스트를 역순으로 처리하여 새로 로드된 기사부터 처리
            for node in reversed(news_nodes):
                if articles_crawled >= ARTICLES_PER_CATEGORY:
                    break

                try:
                    # 광고 요소 건너뛰기
                    if "ad_wrap" in node.get_attribute("class"):
                        continue

                    # 많이 본 기사 건너뛰기
                    try:
                        parent_elements = node.find_elements(By.XPATH, "./ancestor::*")
                        if any("best_view_news_wrap" in parent.get_attribute("class")
                              for parent in parent_elements
                              if parent.get_attribute("class")):
                            continue
                    except:
                        continue

                    # URL 중복 체크
                    link_element = node.find_element(By.TAG_NAME, "a")
                    article_url = link_element.get_attribute("href")

                    if article_url in processed_urls:
                        continue  # 이미 처리된 기사이면 건너뜀

                    # URL이 중복이 아니라면 새로운 기사로 간주
                    new_articles_found = True

                    # 기사 URL 및 제목 추출
                    title_element = node.find_element(By.CSS_SELECTOR, "h3.news_ttl")
                    article_title = title_element.text
                    processed_urls.add(article_url)

                    # 새 탭에서 기사 열기
                    driver.execute_script(f"window.open('{article_url}', '_blank');")
                    driver.switch_to.window(driver.window_handles[-1])
                    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "h2.news_ttl")))

                    # 기사 데이터 추출
                    category_element = driver.find_element(By.CSS_SELECTOR, "span.cate.c_point")
                    author_elements = driver.find_elements(By.CSS_SELECTOR, "dl.author dt.name")
                    email_elements = driver.find_elements(By.CSS_SELECTOR, "dl.author dd.email")
                    time_element = driver.find_element(By.CSS_SELECTOR, "div.time_area dd")

                    # 이미지 추출
                    images_data = []
                    for img_element in driver.find_elements(By.CSS_SELECTOR, "div.thumb_area.img"):
                        try:
                            img = img_element.find_element(By.CSS_SELECTOR, "img")
                            caption = img_element.find_element(By.CSS_SELECTOR, "span.thum_figure_txt")
                            images_data.append({
                                "refid": img_element.get_attribute("refid"),
                                "src": img.get_attribute("src"),
                                "caption": caption.text
                            })
                        except:
                            continue

                    # 시간 형식 변환
                    time_text = time_element.text
                    try:
                        time_parsed = datetime.strptime(time_text, "%Y.%m.%d %H:%M:%S")
                        time_formatted = time_parsed.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        time_formatted = time_text  # 원본 유지

                    # 기사 데이터 생성
                    article_data = {
                        "category": category_element.text,
                        "title": article_title,
                        "url": article_url,
                        "authors": [{"name": author.text, "email": email.text}
                                    for author, email in zip(author_elements, email_elements)],
                        "time": time_formatted,
                        "images": images_data,
                        "content": extract_content(driver)
                    }

                    # 기사 하나를 크롤링할 때마다 바로 저장
                    save_to_hdfs([article_data])
                    articles_crawled += 1
                    logger.info(f"[{category}] {articles_crawled}/{ARTICLES_PER_CATEGORY} 기사 크롤링 및 저장 완료 ({(articles_crawled/ARTICLES_PER_CATEGORY*100):.1f}%)")

                    # 탭 닫기
                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])
                    time.sleep(1)

                except Exception as e:
                    logger.error(f"[{category}] 기사 처리 중 오류: {str(e)}")
                    if len(driver.window_handles) > 1:
                        driver.close()
                        driver.switch_to.window(driver.window_handles[0])
                    continue

            # 새로운 기사를 찾지 못했고, 목표에 도달하지 않았다면 더보기 클릭
            if not new_articles_found and articles_crawled < ARTICLES_PER_CATEGORY:
                try:
                    logger.info(f"[{category}] 더보기 버튼 클릭 시도...")
                    more_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "button.drop_sub_news_btn"))
                    )
                    driver.execute_script("arguments[0].scrollIntoView(); arguments[0].click();", more_button)
                    logger.info(f"[{category}] 더보기 버튼 클릭 성공")
                    time.sleep(2)
                    continue  # 다음 반복으로 넘어가서 새로 로드된 기사 확인
                except Exception as e:
                    logger.error(f"[{category}] 더보기 버튼 클릭 실패: {str(e)}")
                    break

            # 새로운 기사를 찾지 못하고 더보기도 실패했다면 종료
            if not new_articles_found:
                logger.info(f"[{category}] 더 이상 새로운 기사를 찾을 수 없습니다.")
                break

        except Exception as e:
            logger.error(f"[{category}] 크롤링 중 오류 발생: {str(e)}")
            break

logger.info("\n크롤링 작업 완료")
driver.quit()
