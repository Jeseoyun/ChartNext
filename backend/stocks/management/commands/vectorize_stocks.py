import joblib
from django.core.management.base import BaseCommand
from sklearn.feature_extraction.text import TfidfVectorizer
from stocks.models import Stock
from backend import settings
import os


class Command(BaseCommand):
    help = "Vectorize stock data and save to file"

    def handle(self, *args, **kwargs):
        # 1. 경로 확인 및 디렉토리 생성
        vectorizer_path = os.path.join(settings.DATA_ROOT, 'vectorizer.pkl')
        matrix_path = os.path.join(settings.DATA_ROOT, 'tfidf_matrix.pkl')
        ids_path = os.path.join(settings.DATA_ROOT, 'ids.pkl')

        # 디렉토리가 없으면 생성
        os.makedirs(settings.DATA_ROOT, exist_ok=True)

        # 2. 데이터 로드
        stocks = Stock.objects.all()
        if not stocks.exists():
            self.stdout.write(self.style.ERROR("No stock data available in the database."))
            return

        texts = [f"{stock.name} {stock.industry} {stock.sector}" for stock in stocks]
        ids = [stock.id for stock in stocks]

        # 3. TF-IDF 벡터화
        self.stdout.write("Generating vectorizer and TF-IDF matrix...")
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(texts)

        # 4. 파일 저장
        joblib.dump(vectorizer, vectorizer_path)
        joblib.dump(tfidf_matrix, matrix_path)
        joblib.dump(ids, ids_path)

        self.stdout.write(self.style.SUCCESS("Vectorizer and matrix saved successfully!"))