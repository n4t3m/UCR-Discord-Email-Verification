FROM python:latest

COPY . ./usr/app/src
WORKDIR /usr/app/src

RUN pip install -r requirements.txt
RUN pip install -U git+https://github.com/Pycord-Development/pycord

CMD [ "python3", "./bot.py"]