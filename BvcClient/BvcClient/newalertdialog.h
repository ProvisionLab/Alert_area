#ifndef NEWALERTDIALOG_H
#define NEWALERTDIALOG_H

#include <QDialog>
#include "CAlertData.hpp"

namespace Ui {
class NewAlertDialog;
}

class NewAlertDialog : public QDialog
{
    Q_OBJECT

public:
    explicit NewAlertDialog(QWidget *parent = 0);
    ~NewAlertDialog();

public slots:

    void on_NewLD();
    void on_NewVW();
    void on_NewRA();
    void on_Cancel();

public:

    BVC::AlertType  m_alertType;

private:
    Ui::NewAlertDialog *ui;
};

#endif // NEWALERTDIALOG_H
