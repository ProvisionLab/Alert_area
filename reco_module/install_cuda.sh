#!/bin/bash

LSBRELEASE=$(lsb_release -r -s)
ARCH=$(uname -p)

NVIDIACARD=`lspci -mm | grep -i nvidia | xargs printf "%s|" | cut -d "|" -f4`

if [ -z "$NVIDIACARD" ]; then
    echo "no NVIDIA card found"
    exit 1
fi

echo $NVIDIACARD

if [ "$ARCH" = "x86_64" -a "$LSBRELEASE" = "16.04" ]; then
    CUDA_VER=9.0
    CUDA_DISTRO=ubuntu1604
elif [ "$ARCH" = "x86_64" -a "$LSBRELEASE" = "17.04" ]; then
    CUDA_VER=9.0
    CUDA_DISTRO=ubuntu1704
fi

if [ "$CUDA_VER" = "9.1" ]; then

    CUDA_VER_L=9.1.85

    CUDNN_VER=v7.0.5
    CUDNN_VER_S=v7
    CUDNN_DEB_NAME=libcudnn7_7.0.5.15-1+cuda9.1_amd64.deb

elif [ "$CUDA_VER" = "9.0" ]; then

    CUDA_VER_L=9.0.176

    CUDNN_VER=v7.0.5
    CUDNN_VER_S=v7
    CUDNN_DEB_NAME=libcudnn7_7.0.5.15-1+cuda9.0_amd64.deb

elif [ "$CUDA_VER" = "8.0" ]; then

    CUDA_VER=8.0
    CUDA_VER_L=8.0.61

    CUDNN_VER=v6.0
    CUDNN_VER_S=v6
    CUDNN_DEB_NAME=libcudnn7_7.0.5.15-1+cuda8.0_amd64.deb

fi

if [ -z "$CUDA_DISTRO" ]; then
    echo Unsupported Linux version
    exit 1
fi

if [ "$1" = "-u" ] ; then

    if [ ! -z "`cat /usr/local/cuda/version.txt | grep 8.0`" ] ; then    

        echo Uninstalling CUDA 8.0 ...

        sudo apt-get purge --auto-remove -y libcudnn6 
        sudo apt-get purge --auto-remove -y cuda-8-0 
        sudo apt-get purge --auto-remove -y cuda-driver-dev-8-0 
        sudo apt-get purge --auto-remove -y cuda-license-8-0 
        sudo apt-get purge --auto-remove -y cuda-repo-${CUDA_DISTRO}

    elif [ ! -z "`cat /usr/local/cuda/version.txt | grep 9.0`" ] ; then    

        echo Uninstalling CUDA 9.0 ...

        sudo apt-get purge --auto-remove -y libcudnn7
        sudo apt-get purge --auto-remove -y cuda-9-0
        sudo apt-get purge --auto-remove -y cuda-repo-${CUDA_DISTRO}

    elif [ ! -z "`cat /usr/local/cuda/version.txt | grep 9.1`" ] ; then    

        echo Uninstalling CUDA 9.1 ...

        sudo apt-get purge --auto-remove -y libcudnn7
        sudo apt-get purge --auto-remove -y cuda-9-1
        sudo apt-get purge --auto-remove -y cuda-repo-${CUDA_DISTRO}

    else

        echo Uninstalling CUDA ...

        sudo apt-get purge --auto-remove -y cuda
        sudo apt-get purge --auto-remove -y cuda-repo-${CUDA_DISTRO}

    fi
   
    exit 0
fi


sudo apt-get install -y wget

# Install CUDA

if [ ! -f /usr/local/cuda/version.txt ]; then

    echo Ubuntu $LSBRELEASE, Installing CUDA $CUDA_VER_L

    CUDA_DEB_NAME=cuda-repo-${CUDA_DISTRO}_${CUDA_VER_L}-1_amd64.deb

    if [ ! -f $CUDA_DEB_NAME ]; then
        wget "http://developer.download.nvidia.com/compute/cuda/repos/${CUDA_DISTRO}/x86_64/${CUDA_DEB_NAME}" || exit 1
    fi
  
    sudo apt-get install -y linux-headers-$(uname -r)

    sudo dpkg -i $CUDA_DEB_NAME

    sudo apt-key adv --fetch-keys http://developer.download.nvidia.com/compute/cuda/repos/${CUDA_DISTRO}/x86_64/7fa2af80.pub
    sudo apt-get update
    sudo apt-get install -y --no-install-recommends cuda-$CUDA_VER

    rm $CUDA_DEB_NAME

    #if [ ! -f /usr/local/cuda/version.txt ]; then
    #    echo "CUDA $CUDA_VER2" | sudo tee -a /usr/local/cuda/version.txt
    #fi

else
    echo `cat /usr/local/cuda/version.txt` already installed
fi # cuda

# Install cuDNN

if [ -z "`cat /usr/local/cuda/version.txt | grep "$CUDA_VER"`" ]; then
    echo cuDNN $CUDNN_VER require CUDA $CUDA_VER
    exit 1
fi

#if [ -d /usr/local/cuda -a ! -f /usr/local/cuda/lib64/libcudnn.so ]; then
if [ -d /usr/local/cuda ]; then

    echo installing cuDNN

    if [ ! -f $CUDNN_DEB_NAME ] ; then
        echo file $CUDNN_DEB_NAME does not exists, please download it from https://developer.nvidia.com/rdp/cudnn-download
        exit 1
    fi

    if [ -f $CUDNN_DEB_NAME ] ; then

        sudo dpkg -i $CUDNN_DEB_NAME

    else

        CUDNN_TGZ_NAME=cudnn-$CUDA_VER-linux-x64-$CUDNN_VER_S.tgz
        CUDNN_TGZ_URL="http://developer.download.nvidia.com/compute/redist/cudnn/$CUDNN_VER/$CUDNN_TGZ_NAME"

        if [ ! -f $CUDNN_TGZ_NAME ]; then
            wget $CUDNN_TGZ_URL || exit 1
        fi

        sudo tar -xzf $CUDNN_TGZ_NAME -C /usr/local
        sudo ldconfig

        rm $CUDNN_TGZ_NAME
    fi

    CUDNN_MAJOR=`cat /usr/local/cuda/include/cudnn.h | grep "#define CUDNN_MAJOR" | xargs | cut -d ' ' -f3`
    CUDNN_MINOR=`cat /usr/local/cuda/include/cudnn.h | grep "#define CUDNN_MINOR" | xargs | cut -d ' ' -f3`
    
fi

#sudo apt-get install -y libcupti

exit 0
