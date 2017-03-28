FROM python:3

ADD ./Scripts /Scripts

WORKDIR /Scripts

RUN pip install -r requirements.txt

CMD python scheduler.py
