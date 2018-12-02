FROM tdicola/pi_python_opencv_contrib

LABEL maintainer="Sebastian Arboleda <sebasarboleda22@gmail.com"
LABEL Name=web_app 
LABEL Version=0.0.1

COPY ./environments/requirements.txt /

RUN apt-get update #&& apt-get install -y software-properties-common
RUN apt-get autoremove \
    && apt-get autoclean
RUN apt-get install postgresql python-psycopg2 libpq-dev
RUN pip3 install --upgrade setuptools pip
RUN pip3 install -r requirements.txt
RUN apt-get install python3-tk
RUN apt-get install x11vnc

ENV DISPLAY :0

COPY ./ui /ui

COPY ./run.py /

CMD ["python3", "run.py"]
