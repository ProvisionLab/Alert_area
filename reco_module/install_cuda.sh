#!/bin/sh

#lspci -nnk | grep -i nvidia

sudo apt-get install -y wget python3 python3-pip


CUDA_VER=8.0
CUDNN_VER=v6.0

# Install CUDA

if [ ! -f /usr/local/cuda/version.txt ]; then

    echo Installing CUDA

    wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.61-1_amd64.deb" || exit
    sudo dpkg -i cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends cuda-$CUDA_VER
fi

# Install CUDNN

if [ -d /usr/local/cuda -a ! -f /usr/local/cuda/lib64/libcudnn.so ]; then

    echo installing CUDNN

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
