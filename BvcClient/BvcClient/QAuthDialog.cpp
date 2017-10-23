#include "QAuthDialog.h"
#include "ui_qauthdialog.h"

QAuthDialog::QAuthDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::QAuthDialog)
{
    ui->setupUi(this);

    connect(this, &QDialog::finished, [this](int)
    {
        if (result() == QDialog::Accepted)
        {
            m_api_url = ui->m_api_url->text();
            m_username = ui->m_username->text();
            m_password = ui->m_password->text();
        }
    });

    ui->m_username->setFocus();

    ui->m_api_url->setText("http://localhost:5000/");

#ifdef _DEBUG
    ui->m_username->setText("user1");
    ui->m_password->setText("qwerty1");
#endif

}

QAuthDialog::~QAuthDialog()
{
    delete ui;
}

