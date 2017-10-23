#ifndef QAUTHDIALOG_H
#define QAUTHDIALOG_H

#include <QDialog>

namespace Ui {
class QAuthDialog;
}

class QAuthDialog : public QDialog
{
    Q_OBJECT

public:
    explicit QAuthDialog(QWidget *parent = 0);
    ~QAuthDialog();

public:

    QString m_api_url;
    QString m_username;
    QString m_password;

private:
    Ui::QAuthDialog *ui;
};

#endif // QAUTHDIALOG_H
