FROM python:3-alpine

WORKDIR /shop

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip3 install --upgrade pip
COPY ./requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt -i https://pypi.mirrors.ustc.edu.cn/simple/

COPY . .

EXPOSE 8000