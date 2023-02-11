FROM python       

COPY ./requirements.txt /app/requirements.txt
COPY ./app.py /app/app.py
COPY ./test_offers.py /app/test_offers.py
COPY ./wsgi.py /app/wsgi.py
COPY ./run.sh /app/run.sh

WORKDIR /app

RUN pip install -r requirements.txt

ENV PORT=5003
ENV SECRET_KEY=nativa2023

CMD ["gunicorn", "--bind", "0.0.0.0:5003", "wsgi:app"]
