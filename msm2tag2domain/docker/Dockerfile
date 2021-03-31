FROM python:3.8-alpine

# Combine run command to create single intermediate image layer
RUN mkdir -p /usr/src/app \
 && cd /usr/src/app \
# Installing runtime dependencies
 && apk --no-cache add \
      curl \
# Installing buildtime dependencies. They will be removed at end of this
# commands sequence.
 && apk --no-cache add --virtual build-dependencies \
      build-base \
 && apk --no-cache --update add postgresql-dev \
# Updating pip itself before installing packages from requirements.txt
 && pip install --no-cache-dir pip setuptools

# copy py_tag2domain requirements.txt with its dependencies
COPY py_tag2domain/requirements.txt /usr/src/app/requirements.txt
# Installing pip packages from requirements.txt
RUN cd /usr/src/app \
 && pip install --no-cache-dir -r requirements.txt \
# Removing build dependencies leaving image layer clean and neat
 && apk del build-dependencies

# move py_tag2domain library into the right place
COPY py_tag2domain /usr/src/app/py_tag2domain

# move the executable into place
COPY msm2tag2domain/app/msm2tag2domain.py /usr/src/app/msm2tag2domain.py

WORKDIR /usr/src/app

# run command
CMD ["python", "msm2tag2domain.py", "--kafka", "msm2tag2domain.cfg"]

