FROM python:3.10

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /devman-bot-4(lesson-5)

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN chmod -R 777 /star-burger

COPY . .

CMD [ "python", "app.py" ]