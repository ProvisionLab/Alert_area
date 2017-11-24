#!/bin/bash

LSBRELEASE=`lsb_release -r -s`
ARCH=`uname -p`

NVIDIACARD=`lspci -mm | grep -i nvidia | xargs printf "%s|" | cut -d "|" -f4`

if [ -z $NVIDIACARD ]; then
    echo no NVIDIA card found
    exit 1
fi

echo $NVIDIACARD

# Install CUDA

#if [ ! -f /usr/local/cuda/version.txt ]; then

if [ "$ARCH" == "x86_64" -a "$LSBRELEASE" == "16.04" ]; then

    echo Ubuntu $LSBRELEASE, Installing CUDA $CUDA_VER2

    CUDA_VER=8.0
    CUDA_VER2=8.0.61
    CUDNN_VER=v6.0

    sudo apt install -y wget

    DEB_NAME=cuda-repo-ubuntu1604_$CUDA_VER2-1_amd64.deb

    wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/$DEB_NAME" || exit 1

    sudo dpkg -i $DEB_NAME

    sudo apt update
    sudo apt install -y --no-install-recommends cuda-$CUDA_VER

elif [ "$ARCH" == "x86_64" -a "$LSBRELEASE" == "17.04" -o "$LSBRELEASE" == "17.10" ]; then

    echo Ubuntu $LSBRELEASE, Installing CUDA $CUDA_VER2

    CUDA_VER=9.0
    CUDA_VER2=9.0.176
    CUDNN_VER=v6.0

    sudo apt install -y wget

    DEB_NAME=cuda-repo-ubuntu1704_$CUDA_VER2-1_amd64.deb

    wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1704/x86_64/$DEB_NAME" || exit 1

    sudo dpkg -i $DEB_NAME
    sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1704/x86_64/7fa2af80.pub

    sudo apt update
    sudo apt install -y --no-install-recommends cuda-$CUDA_VER

else

    echo Unsupported Linux version
    exit 1

fi # ubuntu release

#else
#    echo `cat /usr/local/cuda/version.txt` already installed
#fi # cuda version

# Install CUDNN

if [ -z "`cat /usr/local/cuda/version.txt | grep $CUDA_VER`" ]; then
    echo CUDNN require CUDA $CUDA_VER
    exit 1
fi

if [ -d /usr/local/cuda -a ! -f /usr/local/cuda/lib64/libcudnn.so ]; then

    echo installing CUDNN

    sudo apt install -y wget

    CUDNN_NAME=cudnn-$CUDA_VER-linux-x64-$CUDNN_VER.tgz

    CUDNN_URL="http://developer.download.nvidia.com/compute/redist/cudnn/$CUDNN_VER/$CUDNN_NAME"
    wget ${CUDNN_URL} || exit 1

    sudo tar -xzf $CUDNN_NAME -C /usr/local

    #sudo mv -v cuda/include/* /usr/local/cuda-$CUDA_VER/include
    #sudo mv -v cuda/lib64/* /usr/local/cuda-$CUDA_VER/lib64

    rm $CUDNN_NAME 
    sudo ldconfig
fi

exit 0
