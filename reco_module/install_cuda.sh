#!/bin/sh

#lspci -nnk | grep -i nvidia

sudo apt-get install -y wget python3 python3-pip


# Install CUDA

if [ ! -d /usr/local/cuda ]; then

    echo installing CUDA

    wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.61-1_amd64.deb" || exit
    sudo dpkg -i cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
    sudo apt-get update
    sudo apt-get install -y cuda
fi

# Install CUDNN

if [ ! -d /usr/local/cuda ]; then

    echo installing CUDNN

    CUDNN_URL="http://developer.download.nvidia.com/compute/redist/cudnn/v5.1/cudnn-8.0-linux-x64-v5.1.tgz"
    wget ${CUDNN_URL} || exit 1
    sudo tar -xzf cudnn-8.0-linux-x64-v5.1.tgz -C /usr/local
    rm cudnn-8.0-linux-x64-v5.1.tgz && sudo ldconfig
fi

exit 0
