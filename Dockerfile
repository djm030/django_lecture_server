# 기본 이미지를 설정합니다. 여기서는 Ubuntu 20.04를 사용합니다.
FROM ubuntu:20.04 AS builder

# 필요한 패키지를 설치합니다.
RUN apt-get update && \
    apt-get install -y python3-pip python3-dev python3-venv \
    build-essential libpq-dev default-libmysqlclient-dev wget \
    zlib1g-dev libncurses5-dev libgdbm-dev libnss3-dev \
    libssl-dev libreadline-dev libffi-dev libsqlite3-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Python 3.11 소스를 다운로드하고 빌드합니다.
RUN wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz && \
    tar xzf Python-3.11.0.tgz && \
    cd Python-3.11.0 && \
    ./configure --enable-optimizations && \
    make altinstall

# 프로젝트 디렉토리를 설정합니다.
ENV APP_HOME /app
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# 가상 환경을 설정합니다.
ENV VIRTUAL_ENV $APP_HOME/venv
RUN python3.11 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# pip, setuptools, wheel을 업그레이드하고 Poetry를 설치합니다.
RUN pip install --no-cache-dir --upgrade pip setuptools wheel
RUN pip install --no-cache-dir "poetry>=1.1.8"

# pyproject.toml과 poetry.lock 파일을 복사합니다.
COPY pyproject.toml poetry.lock ./

# Poetry lock 파일을 업데이트합니다.
RUN poetry lock --no-update

# 의존성을 설치합니다.
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main --extras "mysql"

# 프로젝트의 소스 코드를 복사합니다.
COPY . $APP_HOME

# 포트 8000을 노출합니  다.
EXPOSE 8000

# Gunicorn 서버를 시작합니다.
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--access-logfile", "access.log", "--error-logfile", "error.log"]
