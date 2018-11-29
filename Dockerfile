FROM arm32v7/python:3
ENV DISPLAY :0
LABEL maintainer="Sebastian Arboleda <sebasarboleda22@gmail.com"
LABEL Name=cime_mirror_ui
LABEL Version=0.0.1

COPY ./environments/requirements.txt /

RUN apt-get update \
    && apt-get autoremove \
    && apt-get autoclean \
    && apt-get install -y --no-install-recommends python python-dev python-pip build-essential cmake git pkg-config libjpeg8-dev libtiff5-dev libjasper-dev libpng12-dev libgtk2.0-dev libavcodec-dev libavformat-dev libswscale-dev libv4l-dev libatlas-base-dev gfortran libavresample-dev libgphoto2-dev libgstreamer-plugins-base1.0-dev libdc1394-22-dev  && \
	pip install numpy && \
	cd /opt && \
	git clone https://github.com/opencv/opencv_contrib.git && \
	cd opencv_contrib && \
	git checkout 3.4.0 && \	
	cd /opt && \
	git clone https://github.com/opencv/opencv.git && \
	cd opencv && \
	git checkout 3.4.0 && \
	mkdir build && \
	cd build && \
	cmake 	-D CMAKE_BUILD_TYPE=RELEASE \
		-D BUILD_NEW_PYTHON_SUPPORT=ON \
		-D CMAKE_INSTALL_PREFIX=/usr/local \
		-D INSTALL_C_EXAMPLES=OFF \
		-D INSTALL_PYTHON_EXAMPLES=OFF \
		-D OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib/modules \
		-D PYTHON_EXECUTABLE=/usr/bin/python2.7 \
		-D BUILD_EXAMPLES=OFF /opt/opencv && \
	make -j $(nproc) && \
	make install && \
	ldconfig && \
	apt-get purge -y git && \
	apt-get clean && rm -rf /var/lib/apt/lists/* && \
	rm -rf /opt/opencv*
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt

COPY ./cime_mirror_ui /cime_mirror_ui

COPY ./run.py /

CMD ["python", "run.py"]
