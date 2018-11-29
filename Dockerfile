FROM arm32v7/python:3
ENV DISPLAY :0
LABEL maintainer="Sebastian Arboleda <sebasarboleda22@gmail.com"
LABEL Name=cime_mirror_ui
LABEL Version=0.0.1

COPY ./environments/requirements.txt /

RUN apt-get update \
    && apt-get autoremove \
    && apt-get autoclean \
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY ./cime_mirror_ui /cime_mirror_ui

COPY ./run.py /

CMD ["python", "run.py"]
