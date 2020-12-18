FROM python:3.8

WORKDIR /app
COPY package.json ./
RUN apt-get update && apt-get install -y \
    python3-pip yarn

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY src src
COPY public public

CMD ["python3", "public/main.py"]