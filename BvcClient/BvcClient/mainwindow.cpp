#include "mainwindow.h"
#include "ui_mainwindow.h"
#include "newalertdialog.h"

#include <QListWidgetItem>

#include <QJsonObject>
#include <QJsonArray>
#include "QCameraItem.h"
#include <QMessageBox>
#include "QAuthDialog.h"
#include <QTimer>

MainWindow::MainWindow(QWidget *parent) :
    QMainWindow(parent),
    ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    ui->m_editPanel->hide();

    connect( ui->m_cameraListView, SIGNAL(itemSelectionChanged()), this, SLOT(on_camera_select()));
    connect( ui->m_alertsListView, SIGNAL(itemSelectionChanged()), this, SLOT(on_alert_select()));

    connect( ui->m_bnAddAlert, SIGNAL(clicked()), this, SLOT(on_add_new_alert()));

    QObject::connect( &m_capture, SIGNAL(connected(bool)), this, SLOT(on_camera_connected(bool)));
    QObject::connect( &m_capture, SIGNAL(frameCaptured()), this, SLOT(on_camera_frame()));

    QObject::connect( ui->m_bnCancelAlert, SIGNAL(clicked()), this, SLOT(on_alert_cancel()));
    QObject::connect( ui->m_bnDeleteAlert, SIGNAL(clicked()), this, SLOT(on_alert_delete()));
    QObject::connect( ui->m_bnSaveAlert, SIGNAL(clicked()), this, SLOT(on_alert_save()));

    QObject::connect( ui->m_editor, SIGNAL(require_confirm()), this, SLOT(on_require_confirm()));

    ui->m_durationSlider->setRange(0, 24*60*60);
    QObject::connect( ui->m_durationSlider, SIGNAL(valueChanged(int)), this, SLOT(on_alert_perion_changed(int)));

    ui->m_cameraListView->clear();
    ui->m_alertsListView->clear();
    ui->m_bnAddAlert->hide();
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::showEvent(QShowEvent *e)
{
    QMainWindow::showEvent(e);
    QTimer::singleShot(500, this, SLOT(auth()));
}

void MainWindow::auth()
{
    QAuthDialog dlg;

    if (dlg.exec() != QDialog::Accepted)
    {
        close();
        return;
    }

    m_conn.auth(dlg.m_api_url, dlg.m_username, dlg.m_password, [this](bool succeeded)
    {
        if (succeeded)
            emit on_auth_succeeded();
        else
            emit on_auth_failed();
    });
}

void MainWindow::on_auth_succeeded()
{
    m_conn.get_cameras([this](QJsonObject const & json)
    {
        qDebug() << "get_cameras: " << json;
        on_get_cameras(json["cameras"].toArray());
    });
}

void MainWindow::on_auth_failed()
{
    QMessageBox::about(this, "Auth", "Authorization failed!");
    close();
}

void MainWindow::on_camera_connected(bool bOk)
{
    qDebug() << __FUNCTION__ << bOk;

    if (bOk)
    {
        ui->m_bnAddAlert->show();
        ui->m_editor->setModeNone();
    }
    else
    {
        ui->m_bnAddAlert->hide();
        ui->m_editor->setModeNoConnect();
    }
}

void MainWindow::on_camera_frame()
{
    auto frame = m_capture.get_frame();
    if (frame.data)
    {
        ui->m_editor->showFrame(std::move(frame));
    }
    else
    {
        //qDebug() << "frame dropped";
    }
}

void MainWindow::on_get_cameras(QJsonArray const & json)
{
    qDebug() << __FUNCTION__;

    ui->m_cameraListView->clear();
    ui->m_bnAddAlert->hide();

    for (auto && x : json)
    {
       if (x.isObject())
       {
           auto && j_camera = x.toObject();
           ui->m_cameraListView->addItem(new QCameraItem(j_camera));
       }
    }
}

void MainWindow::on_camera_select()
{
    qDebug() << __FUNCTION__;

    emit on_alert_cancel();

    auto * camera = static_cast<QCameraItem*>(ui->m_cameraListView->currentItem());

    ui->m_alertsListView->clear();
    ui->m_bnAddAlert->hide();

    if (camera)
    {
        ui->m_editor->setModeConnect();

        auto url = camera->get_url();
        if (!url.isEmpty())
        {
            m_capture.start(url, nullptr);
        }

        ui->m_editor->setCamera(camera);

        m_conn.get_camera_alerts(camera->m_Id, [this, camera](QJsonObject const & json)
        {
            qDebug() << "get_camera_alerts: " << json;
            // 2do: check for errors
            try
            {
                camera->set_alerts(json["alerts"].toArray());
            }
            catch (...)
            {
                // invalid json
            }
            emit on_camera_alerts_changed(camera);
        });
    }
}

void MainWindow::on_alert_select()
{
    qDebug() << __FUNCTION__;

    auto * alert = static_cast<QCameraAlertItem*>(ui->m_alertsListView->currentItem());

    if (alert)
    {
        ui->m_editor->setModeEditAlert(alert->m_id);

        if (ui->m_editor->m_new_alert.m_type == BVC::AlertType::LoiteringDetection)
        {
            ui->m_durationSlider->setRange(0, 24*60*60);
            int duration = ui->m_editor->m_new_alert.m_duration;
            ui->m_durationSlider->setValue(duration);
            ui->m_duration_text->setText(QString("%1.%2")
                    .arg(duration / 3600)
                    .arg((duration / 60) % 60, 2, 10, QChar('0')));

            ui->m_duration_panel->show();
        }
        else
            ui->m_duration_panel->hide();

        ui->m_bnCancelAlert->show();
        ui->m_bnDeleteAlert->show();
        ui->m_bnSaveAlert->hide();

        ui->m_editPanel->show();
    }
    else
    {
        ui->m_editor->setModeNone();
        ui->m_editPanel->hide();
    }
}

void MainWindow::on_camera_alerts_changed(QCameraItem* camera)
{
    auto * sel_camera = static_cast<QCameraItem*>(ui->m_cameraListView->currentItem());

    if (camera == sel_camera)
    {
        ui->m_alertsListView->clear();

        for (auto && x : camera->m_alerts)
        {
            QString strName;

            switch(x.m_type)
            {
            case BVC::AlertType::RestrictedArea:
                strName = "RestrictedArea";
                break;
            case BVC::AlertType::LoiteringDetection:
                strName = "LoiteringDetection";
                break;
            case BVC::AlertType::VirtualWall:
                strName = "VirtualWall";
                break;
            default:
                strName = "<invalid alert type>";
            }

            ui->m_alertsListView->addItem(new QCameraAlertItem(camera, x.m_id, strName));
        }
    }
}

void MainWindow::on_add_new_alert()
{
    NewAlertDialog dlg(this);

    if (dlg.exec() != QDialog::Accepted)
        return;

    if (dlg.m_alertType == BVC::AlertType::LoiteringDetection)
    {
        ui->m_durationSlider->setRange(0, 24*60*60);
        ui->m_durationSlider->setValue(0);
        ui->m_duration_text->setText(QString("0.00"));
        ui->m_duration_panel->show();
    }
    else
        ui->m_duration_panel->hide();

    ui->m_bnCancelAlert->show();
    ui->m_bnDeleteAlert->hide();
    ui->m_bnSaveAlert->hide();

    switch (dlg.m_alertType)
    {

    case BVC::AlertType::RestrictedArea:

        // new Restricted Area
        //QMessageBox::about(this, "New Alert", "Draw Restricted Area(s)\nand then Save");
        ui->m_editor->setModeNewAlert(dlg.m_alertType);
        ui->m_editPanel->show();

        break;

    case BVC::AlertType::LoiteringDetection:

        // new Loitering Detection
        ui->m_editor->setModeNewAlert(dlg.m_alertType);
        ui->m_editPanel->show();
        break;

    case BVC::AlertType::VirtualWall:

        {
            // new Virtual Wall

            QMessageBox msgBox(QMessageBox::NoIcon,
                               "New Alert", "Click Line to change direction. 1 click one way, click again direction detection the other way. 3rdclick detection both ways.",
                               QMessageBox::Ok, this,
                               Qt::Dialog);//|Qt::FramelessWindowHint);
            msgBox.exec();

            ui->m_editor->setModeNewAlert(dlg.m_alertType);
            ui->m_editPanel->show();
        }
        break;

    defaut:

        ui->m_editPanel->hide();
        ui->m_editor->setModeNone();
    } // switch
}

void MainWindow::on_alert_cancel()
{
    qDebug() << __FUNCTION__;

    ui->m_editPanel->hide();
    ui->m_editor->setModeNone();
    ui->m_alertsListView->setCurrentItem(nullptr);
}

void MainWindow::on_alert_delete()
{
    qDebug() << __FUNCTION__;

    auto * camera = ui->m_editor->m_pCamera;
    auto alert_id = ui->m_editor->m_new_alert.m_id;

    m_conn.delete_camera_alert(camera->m_Id, alert_id, [this, camera, alert_id](QJsonObject const& j)
    {
        qDebug() << "delete alert reply: ";
        camera->del_alert(alert_id);
        emit on_camera_alerts_changed(camera);
    });

    ui->m_editPanel->hide();
    ui->m_editor->setModeNone();
    ui->m_alertsListView->setCurrentItem(nullptr);
}

void MainWindow::on_alert_save()
{
    qDebug() << __FUNCTION__;

    ui->m_editPanel->hide();

    BVC::CAlertData alert = ui->m_editor->m_new_alert;

    ui->m_editor->setModeNone();
    auto * camera = ui->m_editor->m_pCamera;

    if (alert.m_id.isEmpty())
    {
        // new alert
        m_conn.post_camera_alert(camera->m_Id, alert, [this, camera, alert](QJsonObject const& j)
        {
            qDebug() << "new alert reply: " << j;
            camera->m_alerts.push_back(alert);
            camera->m_alerts.back().set_id(j);
            emit on_camera_alerts_changed(camera);
        });

    }
    else
    {
        // edit alert
        m_conn.update_camera_alert(camera->m_Id, alert.m_id, alert, [this, camera, alert](QJsonObject const& j)
        {
            qDebug() << "update alert reply: " << j;
            camera->update_alert(alert);
            emit on_camera_alerts_changed(camera);
        });

    }

//    ui->m_editor->confirm_new_alert();
}

void MainWindow::on_alert_perion_changed(int value)
{
    qDebug() << __FUNCTION__;

    ui->m_duration_text->setText(QString("%1.%2")
            .arg(value / 3600)
            .arg((value / 60) % 60, 2, 10, QChar('0')));

    if (ui->m_editor->m_new_alert.m_type == BVC::AlertType::LoiteringDetection)
    {
        ui->m_editor->m_new_alert.m_duration = value;
        emit on_require_confirm();
    }
}

void MainWindow::on_require_confirm()
{
    qDebug() << __FUNCTION__;
    ui->m_bnSaveAlert->show();
}
