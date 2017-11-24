#!/bin/bash

USE_CUDA=1

sudo apt update
sudo apt install -y git wget unzip python3  python3-pip
sudo -H pip3 install --upgrade pip

chmod +x install_cuda.sh

if [ "$USE_CUDA" = "1" ]; then

    ./install_cuda.sh || exit

fi

python3 -c "import cv2" > /dev/null

if [ ! $? ]; then

    echo no python3 opencv installed. try install

    sudo apt install -y python3-opencv || echo failed to install python3-opencv
fi

python3 -c "import cv2" > /dev/null

if [ ! $? ]; then

    echo no python3 opencv installed. try build

# build opencv

OPENCV_VER=3.3.0

if [ ! -d ./opencv-$OPENCV_VER ]; then

    echo downloading opencv $OPENCV_VER...

    wget https://github.com/opencv/opencv/archive/$OPENCV_VER.zip || exit

    unzip $OPENCV_VER.zip
    rm $OPENCV_VER.zip

fi

cd opencv-$OPENCV_VER/
mkdir build

cd build/

if [ ! -f ./CMakeCache.txt ]; then

    sudo apt install --assume-yes build-essential cmake git
    sudo apt install --assume-yes pkg-config unzip ffmpeg python-dev python-numpy python3-dev python3-numpy 

    sudo apt install --assume-yes libdc1394-22 libdc1394-22-dev libjpeg-dev libpng12-dev libtiff5-dev libjasper-dev
    sudo apt install --assume-yes libavcodec-dev libavformat-dev libswscale-dev libxine2-dev 
    sudo apt install --assume-yes libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev

    sudo apt install --assume-yes install x264

    echo buildind opencv ...

    cmake -DCMAKE_BUILD_TYPE=RELEASE \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DWITH_FFMPEG=YES \
        -DWITH_CUDA=OFF \
        .. || exit

    make -j $(($(nproc) + 1)) || exit

fi

# Install opencv
sudo make install || exit
sudo /bin/bash -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
sudo ldconfig

cd ../../

fi # build opencv

# Install python dependencies

sudo -H pip3 install -r dependencies.txt

sudo apt install -y python3-tk

# install tensorflow

if [ "$USE_CUDA" = "1" ]; then
    sudo -H pip3 install tensorflow-gpu
else
    sudo -H pip3 install tensorflow
fi

# download tensorflow models

cd object_detection/

if [ ! -d ./ssd_mobilenet_v1_coco_11_06_2017 ]; then

    wget http://download.tensorflow.org/models/object_detection/ssd_mobilenet_v1_coco_11_06_2017.tar.gz || exit
    tar -xf ssd_mobilenet_v1_coco_11_06_2017.tar.gz && rm ssd_mobilenet_v1_coco_11_06_2017.tar.gz

fi

cd ..

chmod +x start.sh
