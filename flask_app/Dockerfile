FROM python:3.8.13-buster
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY ./requirements.txt .

RUN pip install  --default-timeout=1000 --upgrade pip \
    && pip install --default-timeout=1000 --no-cache-dir -r requirements.txt

COPY ./src /app
COPY ./tests/functional /tests

CMD ["python", "/app/utils/pywsgi.py"]
