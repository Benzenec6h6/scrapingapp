FROM python:3.8

EXPOSE 5001

COPY webapp /webapp

WORKDIR /webapp

RUN pip install -r requirements.txt
CMD python app.py