from django.core.management.base import BaseCommand
from stocks.crawler import run_crawler  # 크롤러 함수 임포트

class Command(BaseCommand):
    help = 'Crawl stock data and save it to the database'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting the stock crawler...")
        run_crawler()
        self.stdout.write("Stock crawling completed successfully.")
