#!/bin/bash

USE_CUDA=1


function is_opencv_installed() 
{
    if python3 -c "import cv2" 2> /dev/null ; then return 0 ; else return 1 ; fi
}


sudo apt-get update
sudo apt-get install -y git wget unzip python3 python3-pip
sudo pip3 install --upgrade pip

chmod +x install_cuda.sh

if [ "$USE_CUDA" = "1" ]; then

    ./install_cuda.sh || exit 1

fi

if ! is_opencv_installed ; then

    echo python3 opencv not installed. try install

    sudo apt-get install -y python3-opencv || echo failed to install python3-opencv
fi

if ! is_opencv_installed ; then
    sudo pip3 install opencv-python
fi

if ! is_opencv_installed ; then

    echo python3 opencv not installed. try build

# build opencv

OPENCV_VER=3.3.0

if [ ! -d ./opencv-$OPENCV_VER ]; then

    echo downloading opencv $OPENCV_VER...

    wget https://github.com/opencv/opencv/archive/$OPENCV_VER.zip || exit 1

    unzip $OPENCV_VER.zip
    rm $OPENCV_VER.zip

fi

cd opencv-$OPENCV_VER/
mkdir build

cd build/

if [ ! -f ./CMakeCache.txt ]; then

    sudo apt-get install --assume-yes build-essential cmake git
    sudo apt-get install --assume-yes pkg-config unzip ffmpeg python-dev python-numpy python3-dev python3-numpy 

    sudo apt-get install --assume-yes libdc1394-22 libdc1394-22-dev libjpeg-dev libpng12-dev libtiff5-dev libjasper-dev
    sudo apt-get install --assume-yes libavcodec-dev libavformat-dev libswscale-dev libxine2-dev 
    sudo apt-get install --assume-yes libgstreamer0.10-dev libgstreamer-plugins-base0.10-dev

    sudo apt-get install --assume-yes install x264

    echo buildind opencv ...

    cmake -DCMAKE_BUILD_TYPE=RELEASE \
        -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DWITH_FFMPEG=YES \
        -DWITH_CUDA=OFF \
        -DWITH_JPEG=YES \
        .. || exit 1

    make -j $(($(nproc) + 1)) || echo Failed to build opencv && exit 1

fi

# Install opencv
sudo make install || exit
sudo /bin/bash -c 'echo "/usr/local/lib" > /etc/ld.so.conf.d/opencv.conf'
sudo ldconfig

if ! is_opencv_installed ; then
    echo Failed to install opencv
    exit 1
fi

cd ../../

fi # build opencv

# Install python dependencies

sudo pip3 install --upgrade -r dependencies.txt

# install tensorflow

if [ "$USE_CUDA" = "1" ]; then

    echo Installing Tensorflow, GPU

    PYTHON_REV=$(python3 -V | cut -d ' ' -f2)

    if [ "${PYTHON_REV:0:3}" = "3.5" ]; then

        echo "tensorflow for python 3.5"

        TF_GPU_URL=https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow_gpu-1.5.0-cp35-cp35m-linux_x86_64.whl

        sudo pip3 install --upgrade $TF_GPU_URL

        sudo pip3 install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/protobuf-3.1.0-cp35-none-linux_x86_64.whl

    elif [ "${PYTHON_REV:0:3}" = "3.6" ]; then

        echo "tensorflow for python 3.6"

        TF_GPU_URL=https://storage.googleapis.com/tensorflow/linux/gpu/tensorflow_gpu-1.5.0-cp36-cp36m-linux_x86_64.whl

        sudo pip3 install --upgrade $TF_GPU_URL

        sudo pip3 install --upgrade https://storage.googleapis.com/tensorflow/linux/cpu/protobuf-3.1.0-cp36-none-linux_x86_64.whl

    else
        sudo pip3 install tensorflow-gpu
    fi

else

    echo Installing Tensorflow, CPU

    sudo pip3 install tensorflow
fi

# download tensorflow models

cd object_detection/

MODELNAME=ssd_mobilenet_v1_coco_11_06_2017

if [ ! -d ./$MODELNAME ]; then

    wget http://download.tensorflow.org/models/object_detection/$MODELNAME.tar.gz || exit 1
    tar -xf $MODELNAME.tar.gz && rm $MODELNAME.tar.gz

fi

cd ..

chmod +x *.sh
chmod +x bin/reco_start.bash

# Install Supervisor

sudo apt-get install -y supervisor

sudo ln -s $PWD/reco.spv.conf /etc/supervisor/conf.d/reco.conf

cp reco_config.py.orig reco_config.py

sudo supervisorctl reread
sudo supervisorctl update

