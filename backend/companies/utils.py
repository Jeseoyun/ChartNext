import requests
from bs4 import BeautifulSoup

def get_latest_news(company_name):
    search_url = f"https://news.google.com/search?q={company_name}"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(search_url, headers=headers)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    articles = []
    for item in soup.select('article'):
        title_elem = item.find('h3')
        if title_elem:
            title = title_elem.get_text()
            link = 'https://news.google.com' + title_elem.find('a')['href'][1:]
            articles.append({'title': title, 'link': link})
    return articles 