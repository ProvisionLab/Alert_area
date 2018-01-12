#!/bin/bash

LSBRELEASE=`lsb_release -r -s`
ARCH=`uname -p`

NVIDIACARD=`lspci -mm | grep -i nvidia | xargs printf "%s|" | cut -d "|" -f4`

if [ -z "$NVIDIACARD" ]; then
    echo "no NVIDIA card found"
    exit 1
fi

echo $NVIDIACARD

# Install CUDA

if [ ! -f /usr/local/cuda/version.txt ]; then

if [ "$ARCH" = "x86_64" -a "$LSBRELEASE" = "16.04" ]; then

    CUDA_VER=8.0
    CUDA_VER2=8.0.61
    CUDNN_VER=v6.0

    echo Ubuntu $LSBRELEASE, Installing CUDA $CUDA_VER2

    DEB_NAME=cuda-repo-ubuntu1604_$CUDA_VER2-1_amd64.deb

    if [ ! -f $DEB_NAME ]; then
        sudo apt install -y wget
        wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/$DEB_NAME" || exit 1
    fi

    sudo apt install -y linux-headers-$(uname -r)

    sudo dpkg -i $DEB_NAME

    sudo apt update
    sudo apt install -y --no-install-recommends cuda-$CUDA_VER

elif [ "$ARCH" = "x86_64" -a "$LSBRELEASE" = "17.04" -o "$LSBRELEASE" = "17.10" ]; then

    #echo "Ubuntu $LSBRELEASE not supported"
    #exit 1

# cuda 8
    CUDA_VER=8.0
    CUDA_VER2=8.0.61
    CUDNN_VER=v6.0

# cuda 9
#    CUDA_VER=9.0
#    CUDA_VER2=9.0.176
#    CUDNN_VER=v7.0.4

# cuda 8

    echo Ubuntu $LSBRELEASE, Installing CUDA $CUDA_VER2

    DEB_NAME=cuda-repo-ubuntu1604_$CUDA_VER2-1_amd64.deb

# cuda 9
#    DEB_NAME=cuda-repo-ubuntu1704_$CUDA_VER2-1_amd64.deb

    if [ ! -f $DEB_NAME ]; then
        sudo apt install -y wget
# cuda 8
        wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/$DEB_NAME" || exit 1
# cuda 9
#        wget "http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1704/x86_64/$DEB_NAME" || exit 1
    fi

    sudo apt install -y linux-headers-$(uname -r)

    sudo dpkg -i $DEB_NAME

# cuda 9
#    sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/ubuntu1704/x86_64/7fa2af80.pub

    sudo apt update
    sudo apt install -y --no-install-recommends cuda-$CUDA_VER || exit 1

    if [ ! -f /usr/local/cuda/version.txt ]; then
        echo "CUDA $CUDA_VER2" | sudo tee -a /usr/local/cuda/version.txt
    fi

else

    echo Unsupported Linux version
    exit 1

fi # ubuntu version

else
    echo `cat /usr/local/cuda/version.txt` already installed
fi # cuda version

# Install cuDNN

if [ -z "`cat /usr/local/cuda/version.txt | grep "$CUDA_VER"`" ]; then
    echo cuDNN $CUDNN_VER require CUDA $CUDA_VER
    exit 1
fi

if [ -d /usr/local/cuda -a ! -f /usr/local/cuda/lib64/libcudnn.so ]; then

    echo installing cuDNN

    sudo apt install -y wget

    CUDNN_NAME=cudnn-$CUDA_VER-linux-x64-$CUDNN_VER.tgz

    CUDNN_URL="http://developer.download.nvidia.com/compute/redist/cudnn/$CUDNN_VER/$CUDNN_NAME"

    if [ ! -f $CUDNN_NAME ]; then
        wget ${CUDNN_URL} || exit 1
    fi

    sudo tar -xzf $CUDNN_NAME -C /usr/local

    sudo ldconfig

    CUDNN_MAJOR=`cat /usr/local/cuda/include/cudnn.h | grep "#define CUDNN_MAJOR" | xargs | cut -d ' ' -f3`
    CUDNN_MINOR=`cat /usr/local/cuda/include/cudnn.h | grep "#define CUDNN_MINOR" | xargs | cut -d ' ' -f3`
fi

#sudo apt install -y libcupti-dev

exit 0
