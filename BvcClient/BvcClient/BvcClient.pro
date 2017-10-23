#-------------------------------------------------
#
# Project created by QtCreator 2017-10-18T17:32:55
#
#-------------------------------------------------

QT       += core gui network

greaterThan(QT_MAJOR_VERSION, 4): QT += widgets

TARGET = LvfClient
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

win32 {

    INCLUDEPATH += $$(OPENCV_DIR)\include

    LIBS += -L$$(OPENCV_DIR)\x64\vc14\lib

    contains(DEBUG,1):  LIBS += -lopencv_world320d
    else:               LIBS += -lopencv_world320

    # dll paths to run from qt-creator
    LIBS += -L$$(OPENCV_DIR)\x64\vc14\bin

}
