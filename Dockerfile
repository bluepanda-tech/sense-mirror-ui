FROM tdicola/pi_python_opencv_contrib

LABEL maintainer="Sebastian Arboleda <sebasarboleda22@gmail.com"
LABEL Name=web_app 
LABEL Version=0.0.1

COPY ./environments/requirements.txt /

RUN apt-get update #&& apt-get install -y software-properties-common
#RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 40976EAF437D05B5
#RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 3B4FE6ACC0B21F32
#RUN add-apt-repository "deb http://security.ubuntu.com/ubuntu xenial-security main" && apt-get update
#RUN apt-get install -y --no-install-recommends python3-pip libatlas-base-dev libjasper-dev libqtgui4 python3-pyqt5 libqt4-test \
RUN apt-get autoremove \
    && apt-get autoclean
RUN apt-get install postgresql python-psycopg2 libpq-dev
RUN pip3 install --upgrade setuptools pip
#RUN pip2 install --upgrade pip
RUN pip3 install -r requirements.txt
RUN apt-get install python3-tk
ENV DISPLAY :0
RUN apt-get install x11vnc
COPY ./cime_mirror_ui /cime_mirror_ui

COPY ./run.py /

CMD ["python3", "run.py"]
