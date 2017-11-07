#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

#include "QCvVideoCapure.h"
#include "CConnection.h"

class QCameraItem;


namespace Ui {
class MainWindow;
}

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    explicit MainWindow(QWidget *parent = 0);
    ~MainWindow();

protected:

    void on_get_cameras(QJsonArray const & json);

    void showEvent(QShowEvent *);

    // LD duration time in seconds
    void set_LD_duration(unsigned long duration);

private slots:

    void auth();

    void on_auth_succeeded();
    void on_auth_failed();


    void on_camera_select();
    void on_alert_select();

    void on_camera_alerts_changed(QCameraItem* camera);

    void on_camera_connected(bool bOk);
    void on_camera_frame();

    void on_add_new_alert();

    void on_alert_cancel();
    void on_alert_delete();
    void on_alert_save();

    void on_LD_duration_changed(int value);

    void on_require_confirm();

private:

    Ui::MainWindow *ui;

    BVC::CConnection    m_conn;
    QCvVideoCapure      m_capture;
};

#endif // MAINWINDOW_H
