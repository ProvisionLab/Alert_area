#!/bin/bash

# OpenCV3 for python

function is_opencv_installed() 
{
    if python3 -c "import cv2" 2> /dev/null ; then return 0 ; else return 1 ; fi
}

function get_opencv_version()
{
    local CHECK_OPENCV="import cv2
print(cv2.__version__)"
    CURRENT_OPENCV_VER=`echo "$CHECK_OPENCV" | python3`
}

function is_tensorflow_ok() 
{
    if python3 -c "import tensorflow" 2> /dev/null ; then return 0 ; else return 1 ; fi
}

if is_opencv_installed ; then
    get_opencv_version
    echo "opencv3 - OK. ver: $CURRENT_OPENCV_VER"
else
    echo "opencv3 for python3 not installed."
    echo "try: apt-get install python3-opencv"
    exit 1
fi

# CUDA

# tensorflow

if is_tensorflow_ok ; then
    echo "tensorflow - OK."
else
    echo "tensorflow failed to run."
    exit 1
fi
