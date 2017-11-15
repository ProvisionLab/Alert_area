#!/bin/sh

sudo apt-get update
sudo apt-get install -y git wget python3


# build opencv

sudo apt-get install --assume-yes build-essential cmake git python3
sudo apt-get install --assume-yes pkg-config unzip ffmpeg qtbase5-dev python-dev python3-dev python-numpy python3-numpy
sudo apt-get install --assume-yes libopencv-dev libgtk-3-dev libdc1394-22 libdc1394-22-dev libjpeg-dev libpng12-dev libtiff5-dev libjasper-dev
sudo apt-get install --assume-yes libavcodec-dev libavformat-dev libswscale-dev libxine2-dev libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev
sudo apt-get install --assume-yes libv4l-dev libtbb-dev libfaac-dev libmp3lame-dev libopencore-amrnb-dev libopencore-amrwb-dev libtheora-dev
sudo apt-get install --assume-yes libvorbis-dev libxvidcore-dev v4l-utils python-vtk
sudo apt-get install --assume-yes liblapacke-dev libopenblas-dev checkinstall
sudo apt-get install --assume-yes libgdal-dev

OPENCV_VER=3.3.0

wget https://github.com/opencv/opencv/archive/$(OPENCV_VER).zip

unzip opencv-$(OPENCV_VER).zip
rm opencv-$(OPENCV_VER).zip

cd opencv-$(OPENCV_VER)/
mkdir build

cd build/

cmake -DCMAKE_BUILD_TYPE=RELEASE ^
    -DCMAKE_INSTALL_PREFIX=/usr/local ^
    -DWITH_FFMPEG=YES ^
    ..

make -j $(($(nproc) + 1))

# Install opencv
sudo make install
sudo /bin/bash -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
sudo ldconfig

cd ../../

# Install python dependencies

pip3 install -r dependencies.txt


# Install CUDA

wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.61-1_amd64.deb"
sudo dpkg -i cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
sudo apt-get update
sudo apt-get install cuda

# Install CUDNN

CUDNN_URL="http://developer.download.nvidia.com/compute/redist/cudnn/v5.1/cudnn-8.0-linux-x64-v5.1.tgz"
wget ${CUDNN_URL}
sudo tar -xzf cudnn-8.0-linux-x64-v5.1.tgz -C /usr/local
rm cudnn-8.0-linux-x64-v5.1.tgz && sudo ldconfig

# install tensorflow

pip3 install tensorflow-gpu


# download tensorflow models

cd object_detection/
wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_11_06_2017.tar.gz
tar -xf ssd_mobilenet_v1_coco_11_06_2017.tar.gz
rm ssd_mobilenet_v1_coco_11_06_2017.tar.gz
cd ..

