# 최종 관통 프로젝트

![banner](docs/banner.png)

> **Chart Next** <br /> RAG 기반 뉴스 추천 및 주가 예측 시스템 <br />


<br />
<br />

## Git Guide
<details>
<summary>접기/펼치기</summary>
<div markdown="1">

<br />

1. 깃 클론
```bash
git clone <프로젝트-url>
```
```bash
git clone https://lab.ssafy.com/taeyoun9/04-pjt.git
```

<br />

2. 본인 로컬 브랜치 생성 후 이동
```bash
git switch -c <브랜치명>
```
```bash
git switch -c taeyeong
```

<br />

3. git add
```bash
git add <추가할 파일>
```
```bash
git add .
```

<br />

4. git commit
```bash
git commit -m "<커밋내용>"
```

<br />

5. 로컬 브랜치를 원격 origin에 푸시
```bash
git push -u origin <브랜치명>
```
```
git push -u origin taeyeong
```

> 이후엔 `git push` 만 해도 됨

<br />

6. master 브랜치로 전환
```bash
git switch master
```

<br />

7. master 브랜치가 최신 상태인지 확인
```bash
git pull origin master
```

<br />

8. 본인 브랜치를 master 브랜치에 병합
```bash
git merge taeyeong
```

<br />

9. master에서 git push
```bash
git push
```

</div>
</details>


<br />
<br />

## 실행 방법
<details>
<summary>접기/펼치기</summary>
<div markdown="1">

### 1. 설치 스크립트 실행
```bash
cd scripts
./install.sh
```

### 2. HDFS 설정
```bash
cd backend
poetry install
poetry shell
```

```bash
# 1. HDFS 초기화
hdfs namenode -format
```

```bash
# 2. HDFS 시작
start-dfs.sh
```

```bash
# 3. HDFS 실행 확인 (다음 프로세스들이 보여야 함)
jps
```
- NameNode
- DataNode
- SecondaryNameNode

```bash
# 4. HDFS 디렉토리 구조 생성:
hdfs dfs -mkdir -p /news_data/raw
hdfs dfs -chmod -R 777 /news_data
```

```bash
# 5. HDFS 웹 UI 확인:
http://localhost:9870
```

### 3. 주식데이터 PostgreSQL DB에 삽입
```bash
cd scripts
```

```bash 
psql -U [username] -d [database_name] -f [backup_file].sql
```

```bash
psql -U chart_next_user -d chart_next -f stocks_stock.sql
```
>failed: FATAL:  Peer authentication failed for user "postgres" 오류 발생시 트러블 슈팅 참고

### 4. django 프로젝트 실행
```bash
cd backend
poetry install
poetry shell
python manage.py migrate
python manage.py runserver
```
> poetry install에서 오류날 경우 트러블 슈팅 참고

### 5. vue 프로젝트 실행 
> (새로운 터미널 창에서 진행)
```bash
cd frontend
npm install
npm run dev
```

<br />

### (기타)PostgreSQL 접속 필요시
```bash
# PostgreSQL 접속
sudo -u postgres psql

# 데이터베이스 목록 확인
\l

# chart_next 데이터베이스로 전환
\c chart_next

# SQL문 실행 (예시: 테이블 삭제)
DROP TABLE IF EXISTS news_newsarticle CASCADE;
DROP TABLE IF EXISTS news_newsimage CASCADE;
DROP TABLE IF EXISTS news_newscontent CASCADE;

# 마이그레이션 기록 삭제
DELETE FROM django_migrations WHERE app = 'news';

# PostgreSQL 종료
\q
```

### (기타) PostgreSQL 데이터베이스 재생성
```bash
# PostgreSQL 접속
sudo -u postgres psql

# 기존 연결 종료
SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'chart_next'
AND pid <> pg_backend_pid();

# 데이터베이스 삭제
DROP DATABASE chart_next;

# 데이터베이스 다시 생성
CREATE DATABASE chart_next;

# 권한 부여
GRANT ALL PRIVILEGES ON DATABASE chart_next TO chart_next_user;

# PostgreSQL 종료
\q

# Django 마이그레이션 초기화 및 재적용
cd backend
python manage.py migrate
```

### (기타) 크롤링 한 파일 내용 보기
```bash
hdfs dfs -cat /news_data/raw/articles.json
```

### (기타) 크롤링 한 파일을 로컬로 복사하기
```bash
hdfs dfs -get /news_data/raw/articles.json ./articles.json
```

### (기타) Spark로 HDFS에 있는 크롤링 파일을 PostgreSQL에 로드하기
> backend 디렉토리에서
```bash
spark-submit --jars /usr/local/spark/jars/postgresql-42.7.3.jar news_crawling/spark/load_to_postgres.py
```
  > 또는 프로젝트 루트 디렉토리에서
```bash
spark-submit --jars /usr/local/spark/jars/postgresql-42.7.3.jar backend/news_crawling/spark/load_to_postgres.py
```


### (기타) 로컬에 있는 크롤링 파일을 HDFS에 복사하기
```bash
hdfs dfs -put articles.json /news_data/raw/
```



</div>
</details>


<br />
<br />

## 트러블 슈팅
<details>
<summary>접기/펼치기</summary>
<div markdown="1">

### 1. poetry 오류
`sudo apt install python3-poetry` 로 설치한게 오류가 난 것.

`curl -sSL https://install.python-poetry.org | python3 -` 로 설치하면 해결됨.

우선 apt로 설치한 것을 삭제
```bash
sudo apt remove python3-poetry
sudo apt purge python3-poetry
sudo apt autoremove
```

curl 명령어로 poetry 설치
```bash
curl -sSL https://install.python-poetry.org | python3 -
```

poetry 버전 확인
```bash
$ poetry --version

bash: /usr/bin/poetry: No such file or directory
```

Poetry가 설치되었지만 PATH 설정이 필요한 상황.

다음 단계를 실행하여 해결할 수 있다.

<br />

1. PATH에 Poetry 경로 추가
```bash
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
```

2. 변경사항 적용
```bash
source ~/.bashrc
```

3. Poetry 버전 확인
```bash
poetry --version
```

이제 poetry 명령어가 정상 작동할 것이다.


### 2. jps 했을 때, DataNode 및 NamenNode가 없는 경우
클러스터 ID의 불일치 문제 (이전에 작업한 것과 겹치는 경우 등)

1. 먼저 HDFS를 중지
```bash
stop-dfs.sh
```

2. 기존의 데이터 디렉토리를 삭제
```bash
rm -rf ~/hadoopdata/hdfs/namenode
rm -rf ~/hadoopdata/hdfs/datanode
```

3. NameNode를 다시 포맷
```bash
hdfs namenode -format
```

4. HDFS를 시작
```bash
start-dfs.sh
```

5. 프로세스 확인
```bash
jps
```

이제 다음 프로세스들이 보임
- NameNode
- DataNode
- SecondaryNameNode

### 3. Peer authentication failed for user "postgres"
PostgreSQL의 peer 인증 방식 때문에 발생하는 오류.
WSL 환경에서 다음과 같이 해결 가능

```bash
sudo nano /etc/postgresql/[버전]/main/pg_hba.conf
```
```bash
sudo nano /etc/postgresql/14/main/pg_hba.conf
```

파일에서 다음과 같은 줄들을 찾음
```bash
local   all             postgres                                peer
local   all             all                                     peer
```

이것들을 다음과 같이 변경
```bash
local   all             postgres                                md5
local   all             all                                     md5
```

3. PostgreSQL 재시작
```bash
sudo service postgresql restart
```

</div>
</details>

<br />
<br />

## Commit Rule
`[Update] 변경사항` : 업데이트

`[Create] 파일명` : 생성

`[Delete] 파일명` : 삭제

<br />
<br />

## 명세 만족 사항

- [x] **1. 대규모 데이터 클렌징 및 정규화**  
  - 데이터의 품질을 높이기 위해 중복 제거, 결측치 처리 및 정규화 작업 수행  

<br />

- [x] **2. 데이터 분석, 키워드 추출 및 감성 분석**  
  - pandas를 사용하여 데이터를 분석하고, 중요 키워드 추출  
  - 텍스트 데이터에 대한 감성 분석 수행  

<br />

- [x] **3. 회원가입 기능 구현**  
  - `dj-rest-auth`를 활용하여 회원가입, 로그인, 로그아웃 및 토큰 인증 기능 제공  

<br />

- [x] **4. 데이터 시각화**  
  - pandas, matplotlib, seaborn, plotly를 사용하여 데이터 시각화  
  - 주요 통계 정보 및 트렌드를 그래프로 표현  

<br />

- [x] **5. 시각화 인터페이스 구현**  
  - Streamlit 또는 Vue를 사용해 사용자 친화적인 시각화 인터페이스 구축  

<br />

- [x] **6. 실시간 크롤링 기능**  
  - 실시간 데이터를 수집하여 최신 정보를 반영  

<br />

- [x] **7. 추천 알고리즘 지속 개선**  
  - 추천 알고리즘의 정확도를 높이기 위해 지속적으로 데이터 기반 최적화  

<br />

- [x] **8. 머신러닝 알고리즘 성능 비교 및 최적화**  
  - 3가지 이상의 머신러닝 알고리즘(문자열 매칭, 사용자 행동 패턴 기반 회귀 및 분류)을 비교  
  - 최적의 추천 알고리즘 선정  

<br />

- [x] **9. 최종 기능 구현**  
  - **로그인**: 사용자 인증 및 접근 관리  
  - **뉴스 추천**: 개인화된 뉴스 제공  
  - **게시판**: 사용자 간 소통 및 정보 공유 공간  
  - **RAG 챗봇**: 최신 뉴스를 기반으로 한 검색 및 응답 생성  


<br />
<br />

<!--

## DEMO
> 

![demo1](docs/demo_1.gif) 

<br />

> 


![TIL2](docs/TIL2.png)


<br />
<br />

-->

## 주요 코드

### 구조
```commandline
chart_next_project/
├── frontend/                # Vue.js 프론트엔드
│   ├── src/
│   │   ├── components/     # 재사용 가능한 컴포넌트
│   │   │   └── StockChart.vue  # 주식 차트 컴포넌트
│   │   ├── views/         # 페이지 컴포넌트
│   │   │   ├── HomeView.vue    # 메인 페이지
│   │   │   ├── ChatbotView.vue # 챗봇 페이지
│   │   │   ├── NewsDetailView.vue  # 뉴스 상세 페이지
│   │   │   ├── MainView.vue    # 대시보드 페이지
│   │   │   ├── StockDetailView.vue # 주식 상세 페이지
│   │   │   ├── UserInitView.vue    # 사용자 초기 설정
│   │   │   └── InterestListView.vue # 관심 목록
│   │   └── assets/        # 정적 파일
│   └── package.json
│
├── backend/                # Django 백엔드
│   ├── stocks/            # 주식 관련 앱
│   │   └── management/
│   │       └── commands/  # 커스텀 명령어
│   │           └── crawl_stocks.py  # 주식 크롤링
│   └── manage.py
│
└── scripts/               # 설치 및 설정 스크립트
    └── install.sh         # 설치 스크립트
```
