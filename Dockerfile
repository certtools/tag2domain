FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

EXPOSE 8000
COPY ./api/* /app/

EXPOSE 8000

RUN pip install -r /app/requirements.txt
