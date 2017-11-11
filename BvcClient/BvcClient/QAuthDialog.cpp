#include "QAuthDialog.h"
#include "ui_qauthdialog.h"
#include "auth_config.h"

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

    ui->m_api_url->setText(BVCAPI_URL);

#ifdef _DEBUG
    ui->m_api_url->show();
    ui->m_url_label->show();
    ui->m_username->setText(ROGAPI_USERNAME);
    ui->m_password->setText(ROGAPI_PASSWORD);
#else
    ui->m_api_url->hide();
    ui->m_url_label->hide();
#endif
}

QAuthDialog::~QAuthDialog()
{
    delete ui;
}
