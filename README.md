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

## 환경 설정
<details>
<summary>접기/펼치기</summary>
<div markdown="1">

## 1. Hadoop 설치 및 설정

### 1.1 Java 설치

```bash
sudo apt-get update
sudo apt-get install default-jdk
```

### 1.2 Hadoop 다운로드 및 설치

```bash
wget https://downloads.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz
tar -xzvf hadoop-3.4.0.tar.gz
sudo mv hadoop-3.4.0 /usr/local/hadoop
```

### 1.3 Hadoop 환경 변수 설정

~/.bashrc 파일에 추가:

```bash
# echo 'export PATH=$PATH:/your/custom/path' >> ~/.bashrc
# Hadoop Setting
echo 'export HADOOP_HOME="/usr/local/hadoop"' >> ~/.bashrc
echo 'export PATH="$PATH:$HADOOP_HOME/bin"' >> ~/.bashrc
echo 'export PATH="$PATH:$HADOOP_HOME/sbin"' >> ~/.bashrc
echo 'export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"' >> ~/.bashrc
echo 'export PATH="$PATH:$JAVA_HOME/bin"' >> ~/.bashrc
```

변경사항 적용:

```bash
source ~/.bashrc
```

### 1.4 Hadoop 설정 파일 수정

#### core-site.xml 설정
<!--
```bash
nano $HADOOP_HOME/etc/hadoop/core-site.xml
```

```xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
```
-->

```bash
cat <<EOF > $HADOOP_HOME/etc/hadoop/core-site.xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF
```


#### hdfs-site.xml 설정

<!--
```bash
nano $HADOOP_HOME/etc/hadoop/hdfs-site.xml
```

- 사용자이름 부분에 본인의 리눅스 사용자 이름을 입력하세요.

```xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///home/사용자이름/hadoopdata/hdfs/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///home/사용자이름/hadoopdata/hdfs/datanode</value>
  </property>
</configuration>
```
-->

```bash
cat <<EOF > $HADOOP_HOME/etc/hadoop/hdfs-site.xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///home/사용자이름/hadoopdata/hdfs/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///home/사용자이름/hadoopdata/hdfs/datanode</value>
  </property>
</configuration>
EOF
```

### 1.5 SSH 설정

```bash
sudo apt-get install openssh-server
```

### 1.6 JAVA_HOME 설정
<!-- 
```bash
nano $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

```bash
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64/
``` 
-->
```bash
echo 'export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64/"' >> $HADOOP_HOME/etc/hadoop/hadoop-env.sh
```

### 1.7 HDFS 데이터 디렉토리 생성

```bash
mkdir -p ~/hadoopdata/hdfs/namenode
mkdir -p ~/hadoopdata/hdfs/datanode
```

### 1.8 HDFS 포맷

```bash
hdfs namenode -format
```

### 1.8-1 ssh 키 생성
ssh-keygen -t rsa
cat ~/.ssh/id_rsa.pub >> ~/.ssh/authorized_keys

### 1.9 HDFS 데몬 시작

```bash
start-dfs.sh
```

#### 1.9.1 데몬 실행 확인

```bash
jps
```

`NameNode`, `DataNode`, `SecondaryNameNode`가 실행 중인지 확인합니다.

### 1.10 HDFS 사용해보기

#### 1.10.1 디렉토리 생성

```bash
hdfs dfs -mkdir /user
hdfs dfs -mkdir /user/사용자이름
```

#### 1.10.2 파일 목록 확인

```bash
hdfs dfs -ls /user/사용자이름/
```

### 1.11 HDFS 데몬 종료

```bash
stop-dfs.sh
```

## 2. Spark 설치 및 설정

### 2.1 Spark 다운로드 및 설치

1. Apache Spark 공식 사이트에서 파일 다운로드
```bash
wget https://dlcdn.apache.org/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz
```

2. 압축 해제 및 설치:
```bash
tar xvzf spark-3.5.3-bin-hadoop3.tgz
sudo mv spark-3.5.3-bin-hadoop3 /usr/local/spark
```

### 2.2 Spark 환경 변수 설정

~/.bashrc 파일에 추가:

```bash
# Spark Setting
echo 'export SPARK_HOME="/usr/local/spark"' >> ~/.bashrc
echo 'export PATH="$PATH:$SPARK_HOME/bin"' >> ~/.bashrc
```

변경사항 적용:

```bash
source ~/.bashrc
```

## 3. 프로젝트 의존성 관리

Poetry를 사용하여 프로젝트 의존성을 관리합니다.

```bash
# Poetry 설치 (필요한 경우)
curl -sSL https://install.python-poetry.org | python3 -

# 의존성 설치 (pjt폴더로 이동 후)
poetry install

# 가상환경 활성화
poetry shell
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
├── chart_next/       # Django 프로젝트 폴더
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── accounts/         # 사용자 인증 및 관리 앱
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── stock/            # 주식 데이터 및 뉴스 관련 앱
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── utils.py
│   ├── views.py
│   ├── urls.py
│   └── migrations/
├── manage.py
└── frontend/         # Vue 3 + Vite 프론트엔드 폴더
    ├── index.html
    ├── package.json
    ├── vite.config.js
    └── src/
        ├── main.js
        ├── App.vue
        ├── axios.js
        ├── router/
        │   └── index.js
        ├── store/
        │   └── index.js
        └── components/
            ├── Home.vue
            ├── Register.vue
            ├── Login.vue
            ├── InterestedCompanies.vue
            ├── StockChart.vue
            └── CompanyNews.vue
```

<br />


### 1. chatbot.py
> 

<br />

### 2. document_store.py
> 

<br />

### 3. preprocessing.py
> 

<br />

### 4. pyproject.toml
> 

<br />

### 5. poetry.lock
> 