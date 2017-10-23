#include "newalertdialog.h"
#include "ui_newalertdialog.h"

NewAlertDialog::NewAlertDialog(QWidget *parent) :
    QDialog(parent),
    ui(new Ui::NewAlertDialog)
{
    ui->setupUi(this);

    connect(ui->m_bnCancel, SIGNAL(clicked()), this, SLOT(on_Cancel()));
    connect(ui->m_bnLD, SIGNAL(clicked()), this, SLOT(on_NewLD()));
    connect(ui->m_bnVW, SIGNAL(clicked()), this, SLOT(on_NewVW()));
    connect(ui->m_bnRA, SIGNAL(clicked()), this, SLOT(on_NewRA()));
}

NewAlertDialog::~NewAlertDialog()
{
    delete ui;
}

void NewAlertDialog::on_NewLD()
{
    m_alertType = BVC::AlertType::LoiteringDetection;
    accept();
}

void NewAlertDialog::on_NewVW()
{
    m_alertType = BVC::AlertType::VirtualWall;
    accept();
}

void NewAlertDialog::on_NewRA()
{
    m_alertType = BVC::AlertType::RestrictedArea;
    accept();
}

void NewAlertDialog::on_Cancel()
{
    m_alertType = BVC::AlertType::None;
    reject();
}
