FROM python:3.13-alpine

WORKDIR /rds

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

VOLUME [ "/rds/data" ]

CMD ["python", "src/discord-bot.py"]

