#-------------------------------------------------
#
# Project created by QtCreator 2017-10-18T17:32:55
#
#-------------------------------------------------

QT       += core gui network

CONFIG -= debug_and_release

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = BvcClient
TEMPLATE = app

# The following define makes your compiler emit warnings if you use
# any feature of Qt which as been marked as deprecated (the exact warnings
# depend on your compiler). Please consult the documentation of the
# deprecated API in order to know how to port your code away from it.
DEFINES += QT_DEPRECATED_WARNINGS

# You can also make your code fail to compile if you use deprecated APIs.
# In order to do so, uncomment the following line.
# You can also select to disable deprecated APIs only up to a certain version of Qt.
#DEFINES += QT_DISABLE_DEPRECATED_BEFORE=0x060000    # disables all the APIs deprecated before Qt 6.0.0


SOURCES += main.cpp\
        mainwindow.cpp \
    QCameraItem.cpp \
    QCvImageWidget.cpp \
    CConnection.cpp \
    QCameraFrameWidget.cpp \
    newalertdialog.cpp \
    QCvVideoCapure.cpp \
    CAlertData.cpp \
    QAuthDialog.cpp

HEADERS  += mainwindow.h \
    QCameraItem.h \
    QCvImageWidget.h \
    CConnection.h \
    QCameraFrameWidget.h \
    newalertdialog.h \
    QCvVideoCapure.h \
    QAuthDialog.h \
    CAlertData.hpp

FORMS    += mainwindow.ui \
    newalertdialog.ui \
    qauthdialog.ui

win32-msvc* {

    MSVC_VER = $$(VisualStudioVersion)

    #equals(MSVC_VER, 14.0) {

        # linking with opencv 3.2

        INCLUDEPATH += $$(OPENCV_DIR)\include

        LIBS += -L$$(OPENCV_DIR)\x64\vc14\lib

        contains(DEBUG,1):  LIBS += -lopencv_world320d
        else:               LIBS += -lopencv_world320

        # dll paths to run from qt-creator
        LIBS += -L$$(OPENCV_DIR)\x64\vc14\bin
    #}
}

unix {

    # (recomended) use this if ubuntu opencv-dev package is installed ( apt-get install libopencv-dev )
    CONFIG += link_pkgconfig
    PKGCONFIG += opencv

    # use this if custom opencv build is installed ( download & cmake & make install )
#    INCLUDEPATH += /usr/local/include
#    LIBS += -L/usr/local/lib -lopencv_core -lopencv_videoio -lopencv_imgproc

}

mac {

    # make sure PATH contains pkg-config & PKG_CONFIG_PATH is defined
    CONFIG += link_pkgconfig
    PKGCONFIG += opencv
}
