from django.core.management.base import BaseCommand
from django.core.management import call_command

class Command(BaseCommand):
    help = '초기 주식 데이터를 데이터베이스에 로드합니다.'

    def handle(self, *args, **kwargs):
        try:
            call_command('loaddata', 'initial_stocks.json')
            self.stdout.write(self.style.SUCCESS('성공적으로 주식 데이터를 로드했습니다.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'데이터 로드 중 오류가 발생했습니다: {str(e)}')) 