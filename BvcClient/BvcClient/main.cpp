#include "mainwindow.h"
#include <QApplication>
#include "auth_config.h"

int main(int argc, char *argv[])
{
    QApplication a(argc, argv);

    QApplication::setOrganizationName(COMPANY_NAME);
    QApplication::setApplicationName(APP_NAME);

    a.setWindowIcon(QIcon(":/rog_256.ico"));
    MainWindow w;
    w.show();

    return a.exec();
}
