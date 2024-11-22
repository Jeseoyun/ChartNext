from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import time
from .models import Stock  # Django 모델 가져오기

def crawl_page(driver, market):
    data = []
    soup = BeautifulSoup(driver.page_source, "html.parser")
    rows = soup.select("#screenerTableWrapper > table > tbody > tr")
    for row in rows:
        try:
            code = row.select_one("th > div.flex.items-center > a").text.strip()
            name = row.select_one("td:nth-child(2)").text.strip()
            exchange = row.select_one("td:nth-child(3)").text.strip()
            sector = row.select_one("td:nth-child(4)").text.strip()
            industry = row.select_one("td:nth-child(5)").text.strip()
            data.append({
                "code": code,
                "name": name,
                "exchange": exchange,
                "sector": sector,
                "industry": industry,
                "market": market
            })
        except AttributeError:
            continue
    print(data)
    return data

def crawl_stocks(driver, country="South Korea"):
    base_url = "https://kr.investing.com/stock-screener"
    driver.get(base_url)
    time.sleep(1)
    
    market = "Domestic" if country == "South Korea" else "International"
    
    if country == "United States":
        driver.execute_script("window.scrollTo(0, 0);")  # 스크롤을 가장 위로 올림
        time.sleep(5)
        country_selector = driver.find_element(By.CSS_SELECTOR, '#screenerControls > div.flex.items-center.gap-4 > div.relative > div > button')
        country_selector.click()
        time.sleep(10)
    
    while True:
        data = crawl_page(driver, market)
        for entry in data:
            # 중복 여부 확인
            if not Stock.objects.filter(code=entry['code']).exists():
                Stock.objects.create(**entry)  # Django 모델에 저장
        try:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight*0.4);")  # 스크롤을 중간으로 내림
            time.sleep(1)
            next_button = driver.find_element(By.CSS_SELECTOR, '#__next > div.md\:relative.md\:bg-white > div.font-sans-v2.text-\[\#181c21\].antialiased.xl\:container.md\:px-7.md2\:px-8.xl\:mx-auto > div:nth-child(2) > div.my-6.flex.items-center > div.flex.px-2.md\:px-0.flex-2.justify-center > div > ul > li.flex.items-center.gap-1\.5.rounded.text-sm\/5.font-semibold.md\:bg-\[\#F7F7F8\].md\:pl-5.md\:pr-2\.5.h-\[34px\].cursor-pointer.text-inv-blue-500')
            # 버튼이 비활성화되어 있는지 확인
            if "disabled" in next_button.get_attribute("class"):
                print("No more pages to navigate.")
                break
            # JavaScript로 클릭 이벤트 트리거
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(5)
        except Exception as e:
            print(f"No more pages or error in navigating to next page: {e}")
            break

def run_crawler():
    driver_path = "/usr/local/bin/chromedriver-linux64"
    options = webdriver.ChromeOptions()
    options.binary_location = driver_path  # 크롬 드라이버 경로 설정

    driver = webdriver.Chrome(options=options)  # 옵션 객체를 사용하여 드라이버 초기화
    
    
    try:
        print("Crawling South Korea stocks...")
        crawl_stocks(driver, "South Korea")

        print("Crawling US stocks...")
        crawl_stocks(driver, "United States")
        
        print("Crawling complete.")
    finally:
        driver.quit()
