FROM arm32v7/python:3

LABEL maintainer="Sebastian Arboleda <sebasarboleda22@gmail.com"
LABEL Name=cime_mirror_engine 
LABEL Version=0.0.1

COPY ./environments/requirements.txt /

RUN apt-get update
RUN apt-get install --no-recommends libatlas-base-dev libjasper-dev libqtgui4 python3-pyqt5 libqt4-test \
    && apt-get autoremove \
    && apt-get autoclean \
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY ./cime_mirror_engine /cime_mirror_engine

COPY ./run.py /

CMD ["python", "run.py"]
