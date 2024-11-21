#!/bin/bash

# 시스템 업데이트
echo "시스템 업데이트 중..."
sudo apt update
sudo apt upgrade -y

# Java 설치
echo "Java 설치 중..."
sudo apt-get install -y default-jdk

# pip 설치
echo "pip 설치 중..."
sudo apt install -y python3-pip

# poetry 설치
echo "poetry 설치 중..."
sudo apt install -y python3-poetry

# nvm 설치
echo "nvm 설치 중..."
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install --lts
nvm alias default lts

# Kafka 설치
echo "Kafka 설치 중..."
curl -O https://downloads.apache.org/kafka/3.9.0/kafka_2.13-3.9.0.tgz
tar -xzf kafka_2.13-3.9.0.tgz
sudo mv kafka_2.13-3.9.0 /usr/local/kafka
rm kafka_2.13-3.9.0.tgz

# Hadoop 설치
echo "Hadoop 설치 중..."
curl -O https://downloads.apache.org/hadoop/common/hadoop-3.4.0/hadoop-3.4.0.tar.gz
tar -xzvf hadoop-3.4.0.tar.gz
sudo mv hadoop-3.4.0 /usr/local/hadoop
rm hadoop-3.4.0.tar.gz

# Hadoop 환경 변수 설정
echo "Hadoop 환경 변수 설정 중..."
echo 'export HADOOP_HOME="/usr/local/hadoop"' >> ~/.bashrc
echo 'export PATH="$PATH:$HADOOP_HOME/bin:$HADOOP_HOME/sbin"' >> ~/.bashrc
echo 'export JAVA_HOME="/usr/lib/jvm/java-11-openjdk-amd64"' >> ~/.bashrc
echo 'export PATH="$PATH:$JAVA_HOME/bin"' >> ~/.bashrc

# Hadoop 설정 파일 수정
echo "Hadoop 설정 파일 수정 중..."
cat <<EOF > /usr/local/hadoop/etc/hadoop/core-site.xml
<configuration>
    <property>
        <name>fs.defaultFS</name>
        <value>hdfs://localhost:9000</value>
    </property>
</configuration>
EOF

cat <<EOF > /usr/local/hadoop/etc/hadoop/hdfs-site.xml
<configuration>
  <property>
    <name>dfs.replication</name>
    <value>1</value>
  </property>
  <property>
    <name>dfs.namenode.name.dir</name>
    <value>file:///home/$USER/hadoopdata/hdfs/namenode</value>
  </property>
  <property>
    <name>dfs.datanode.data.dir</name>
    <value>file:///home/$USER/hadoopdata/hdfs/datanode</value>
  </property>
</configuration>
EOF

# HDFS 데이터 디렉토리 생성
echo "HDFS 데이터 디렉토리 생성 중..."
mkdir -p ~/hadoopdata/hdfs/namenode
mkdir -p ~/hadoopdata/hdfs/datanode

# Spark 설치
echo "Spark 설치 중..."
curl -O https://dlcdn.apache.org/spark/spark-3.5.3/spark-3.5.3-bin-hadoop3.tgz
tar -xzvf spark-3.5.3-bin-hadoop3.tgz
sudo mv spark-3.5.3-bin-hadoop3 /usr/local/spark
rm spark-3.5.3-bin-hadoop3.tgz

# Spark 환경 변수 설정
echo "Spark 환경 변수 설정 중..."
echo 'export SPARK_HOME="/usr/local/spark"' >> ~/.bashrc
echo 'export PATH="$PATH:$SPARK_HOME/bin"' >> ~/.bashrc

# PostgreSQL 설치
echo "PostgreSQL 설치 중..."
sudo apt install -y postgresql postgresql-contrib
sudo service postgresql start

# PostgreSQL 데이터베이스 및 사용자 생성
echo "PostgreSQL 데이터베이스 및 사용자 생성 중..."
sudo -u postgres psql <<EOF
CREATE DATABASE chart_next;
CREATE USER chart_next_user WITH PASSWORD '123qweasd';
ALTER ROLE chart_next_user SET client_encoding TO 'utf8';
ALTER ROLE chart_next_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE chart_next_user SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE chart_next TO chart_next_user;
\q
EOF

# 변경 사항 적용
source ~/.bashrc

echo "설치가 완료되었습니다. 이제 Chart Next를 실행할 준비가 되었습니다."