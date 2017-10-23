#ifndef QCAMERAFRAMEWIDGET_H
#define QCAMERAFRAMEWIDGET_H

#include "QCvImageWidget.h"
#include "QCameraItem.h"

class QCameraFrameWidget : public QCvImageWidget
{
    Q_OBJECT

public:

    enum QCameraFrameMode
    {
        EditNone,
        EditConnect,
        EditNewAlert,
        EditEditAlert,
        EditConfirm,
    };


public:

    QCameraFrameWidget(QWidget *parent = 0);

    void setCamera(QCameraItem * pCamera);

    void setModeNone();
    void setModeConnect();
    void setModeNoConnect();
    void setModeNewAlert(BVC::AlertType alertType);
    void setModeEditAlert(QString alert_id);

protected:

    void postProcessImage(QPixmap & img) override;

    void drawAlert(QPainter & paint, BVC::CAlertData const & alert, bool bDragMode);
    void drawArrow(QPainter & paint, QPoint const & p1, QPoint const & p2);

    bool is_point_on_line(QPointF pt, QPointF p1, QPointF p2);

private:

    void mousePressEvent(QMouseEvent *event);
    void mouseReleaseEvent(QMouseEvent *event);
    void mouseMoveEvent(QMouseEvent * event);

signals:

    void require_confirm();

public slots:

    void confirm_new_alert();

public:

    QCameraFrameMode m_mode;
    QCameraItem * m_pCamera;

    BVC::CAlertData m_new_alert;

    bool m_bDragPoint;
    int  m_nDragIndex;
};

#endif // QCAMERAFRAMEWIDGET_H
