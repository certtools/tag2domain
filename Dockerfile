#
#
# Run me as:
#
# docker build -t tag2domain_api:0.3 .
# 
# Then run the image via:
# docker run -d -p 80:8000 -e PORT="8000" --name api -it tag2domain_api:0.3

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

EXPOSE 8000
COPY ./api/* /app/

RUN pip install -r /app/requirements.txt
