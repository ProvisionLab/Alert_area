#include "mainwindow.h"
#include <QApplication>

#define COMPANY_NAME    "ROG Security, Inc."
#define APPNAME         "ROG Tool"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    QApplication::setOrganizationName(COMPANY_NAME);
    QApplication::setApplicationName(APPNAME);

    a.setWindowIcon(QIcon(":/rog_256.ico"));
    MainWindow w;
    w.show();

    return a.exec();
}
