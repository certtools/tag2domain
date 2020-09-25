#
#
# Run me as:
#
# docker build -t tag2domain_api:0.4 .
# 
# Then run the image via:
# docker run -d -p 80:8001 -e PORT="8001" --name api -it tag2domain_api:0.4

FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7

EXPOSE 8001
COPY ./api/* /app/

RUN pip install -r /app/requirements.txt

HEALTHCHECK --interval=5m --timeout=3s  CMD curl -f http://localhost:8000/test/self-test || exit 1
