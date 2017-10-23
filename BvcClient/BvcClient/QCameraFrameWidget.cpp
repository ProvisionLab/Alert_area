#include "QCameraFrameWidget.h"
#include <QPainter>
#include <QDebug>

QCameraFrameWidget::QCameraFrameWidget(QWidget *parent)
    : QCvImageWidget(parent)
    , m_pCamera(nullptr)
    , m_mode(EditNone)
    , m_bDragPoint(false)
{
    setMouseTracking(true);
}

void QCameraFrameWidget::setModeConnect()
{
    setPixmap(QPixmap());
    m_lastFrame.release();

    setText("Connection...");

    m_mode = QCameraFrameMode::EditConnect;
}

void QCameraFrameWidget::setModeNoConnect()
{
    setPixmap(QPixmap());
    m_lastFrame.release();

    setText("no connection");

    m_mode = QCameraFrameMode::EditConnect;
}

void QCameraFrameWidget::setModeNone()
{
    m_new_alert.reset();

    m_bDragPoint = false;

    m_mode = QCameraFrameMode::EditNone;
}


bool QCameraFrameWidget::is_point_on_line(QPointF pt, QPointF p1, QPointF p2)
{
    QPointF dp;

    dp = p1 - pt;
    if (abs(dp.x()) < 4 && abs(dp.y()) < 4)
        return false;

    dp = p2 - pt;
    if (abs(dp.x()) < 4 && abs(dp.y()) < 4)
        return false;

    QVector2D v0(pt-p1);
    QVector2D v1(p2-p1);

    if (v1.lengthSquared() < 4*4)
        return false;

    float M = v1.length();

    float x = QVector2D::dotProduct(v1,v0)/M;
    //float y = v0.distanceToLine(QVector2D(0,0), v1);
    float y = (v1.x()*v0.y() - v1.y() * v0.x())/M;

    if (abs(y) < 4 && x > 0 && x < M)
        return true;

    return false;
}

void QCameraFrameWidget::drawArrow(QPainter & paint, QPoint const & p1, QPoint const & p2)
{
    const float m = 4.0f;

    QVector2D v1(p2 - p1);
    if (v1.lengthSquared() < 4*m*m)
        return;

    v1.normalize();

    QVector2D v2(v1.y(), -v1.x());
    v2.normalize();

    QVector2D c((p1 + p2)/2);

    paint.drawLine( (c + v1 * m).toPointF(), (c + v1 * m + v2 * (2*m)).toPointF());
    paint.drawLine( (c - v1 * m).toPointF(), (c - v1 * m + v2 * (2*m)).toPointF());
    paint.drawLine( (c + v2 * (3*m)).toPointF(), (c + v1 * (2*m)+ v2 * m).toPointF());
    paint.drawLine( (c + v2 * (3*m)).toPointF(), (c - v1 * (2*m)+ v2 * m).toPointF());
}

void QCameraFrameWidget::drawAlert(QPainter & paint, BVC::CAlertData const & alert, bool bDragMode)
{
    std::vector<QPoint> points;
    points.reserve(alert.m_points.size());

    int w = paint.window().width();
    int h = paint.window().height();

    for (auto && p : alert.m_points)
    {
        points.push_back({int(p.x * w), int(p.y * h)});
    }

    if (alert.m_type == BVC::AlertType::RestrictedArea)
    {
        if (bDragMode)
        {
            paint.drawPolyline(points.data(), (int)points.size());
        }
        else
        {
            paint.drawPolygon(points.data(), (int)points.size());
        }
    }

    if (alert.m_type == BVC::AlertType::LoiteringDetection)
    {
        if (bDragMode)
        {
            paint.drawPolyline(points.data(), (int)points.size());
        }
        else
        {
            paint.drawPolygon(points.data(), (int)points.size());
        }
    }

    if (alert.m_type == BVC::AlertType::VirtualWall)
    {
        if (points.size() >= 2)
        {
            paint.drawLine(points[0], points[1]);

            if(alert.m_direction == BVC::AlertDirection::Both || alert.m_direction == BVC::AlertDirection::ToLeft)
                drawArrow(paint, points[0], points[1]);

            if(alert.m_direction == BVC::AlertDirection::Both || alert.m_direction == BVC::AlertDirection::ToRight)
                drawArrow(paint, points[1], points[0]);
        }
    }
}

void QCameraFrameWidget::postProcessImage(QPixmap & img)
{
    if (!m_pCamera)
        return;

    if(m_pCamera->m_alerts.empty() && m_new_alert.m_points.size() < 2)
        return;

    QPainter paint(&img);

    QPen penSel(QColor(255,0,255,255));
    QPen penRA(QColor(255,0,0,255));
    QPen penLD(QColor(0,0,255,255));
    QPen penVW(QColor(0,255,0,255));

    QBrush brushSel(QColor(255,128,255,255), Qt::DiagCrossPattern);
    QBrush brushRA(QColor(255,128,128,255), Qt::DiagCrossPattern);
    QBrush brushLD(QColor(128,128,255,255), Qt::DiagCrossPattern);

    for (auto && alert : m_pCamera->m_alerts)
    {
        if (alert.m_id == m_new_alert.m_id)
        {
            continue;
            //paint.setPen(penSel);
            //paint.setBrush(brushSel);
        }
        else
        {
            switch(alert.m_type)
            {
            case BVC::AlertType::RestrictedArea:
                paint.setPen(penRA);
                paint.setBrush(brushRA);
                break;
            case BVC::AlertType::LoiteringDetection:
                paint.setPen(penLD);
                paint.setBrush(brushLD);
                break;
            case BVC::AlertType::VirtualWall:
                paint.setPen(penVW);
                break;
            }
        }

        drawAlert(paint, alert, false);
    }

    if (m_new_alert.m_points.size() >= 2)
    {
        paint.setPen(penSel);
        paint.setBrush(brushSel);

        drawAlert(paint, m_new_alert, m_mode == EditNewAlert);
    }
}

void QCameraFrameWidget::setCamera(QCameraItem * pCamera)
{
    m_pCamera = pCamera;
    m_new_alert.reset();
}

void QCameraFrameWidget::setModeNewAlert(BVC::AlertType alertType)
{
    m_new_alert.reset();
    m_new_alert.m_type = alertType;

    m_bDragPoint = false;

    m_mode = QCameraFrameMode::EditNewAlert;
}

void QCameraFrameWidget::setModeEditAlert(QString alert_id)
{
    for (auto && alert : m_pCamera->m_alerts)
    {
        if (alert.m_id == alert_id)
        {
            m_new_alert = alert;
        }
    }

    m_bDragPoint = false;

    m_mode = QCameraFrameMode::EditEditAlert;
}

void QCameraFrameWidget::mousePressEvent(QMouseEvent *event)
{
    qDebug() << __FUNCTION__;

    if (event->button() == Qt::LeftButton)
    {
        auto p = widget2rel(event->pos());

        if (m_mode == EditNewAlert)
        {
            if (m_new_alert.m_type == BVC::AlertType::VirtualWall)
            {
                if (m_new_alert.m_points.size() == 2)
                {
                    m_new_alert.m_points.back() = p;
                    m_mode = EditConfirm;
                    processFrame(m_lastFrame);
                    emit require_confirm();
                    return;
                }
            }
            else
            {
                if (m_new_alert.m_points.size() > 0)
                {
                    auto p0 = rel2widget(m_new_alert.m_points.front());
                    auto dp = p0 - event->pos();
                    if (abs(dp.x()) < 4 && abs(dp.y()) < 4)
                    {
                        // close polygone
                        m_mode = EditConfirm;
                        m_new_alert.m_points.pop_back();
                        processFrame(m_lastFrame);
                        emit require_confirm();
                        return;
                    }
                }
            }

            if (m_new_alert.m_points.empty())
            {
                m_new_alert.m_points.push_back(p);
            }
            else
            {
                m_new_alert.m_points.back() = p;
            }

            m_new_alert.m_points.push_back(p);
            processFrame(m_lastFrame);
        }

        if (m_mode == EditEditAlert)
        {
            for (int i = 0; i < (int)m_new_alert.m_points.size(); ++i)
            {
                auto p0 = rel2widget(m_new_alert.m_points[i]);
                auto dp = p0 - event->pos();
                if (abs(dp.x()) < 4 && abs(dp.y()) < 4)
                {
                    m_bDragPoint = true;
                    m_nDragIndex = i;
                    return;
                }

            }
        }

        if (m_new_alert.m_type == BVC::AlertType::VirtualWall)
        {
            if ((m_mode == EditEditAlert || m_mode == EditConfirm) && m_new_alert.m_points.size() == 2)
            {
                if ( is_point_on_line(event->pos(), rel2widget(m_new_alert.m_points[0]), rel2widget(m_new_alert.m_points[1])))
                {
                    switch (m_new_alert.m_direction)
                    {
                    case BVC::AlertDirection::Both:
                        m_new_alert.m_direction = BVC::AlertDirection::ToLeft;
                        break;
                    case BVC::AlertDirection::ToLeft:
                        m_new_alert.m_direction = BVC::AlertDirection::ToRight;
                        break;
                    case BVC::AlertDirection::ToRight:
                        m_new_alert.m_direction = BVC::AlertDirection::Both;
                        break;
                    }
                    processFrame(m_lastFrame);
                    emit require_confirm();
                }
            }
        }

    }

    else if (event->button() == Qt::RightButton)
    {
    }
}

void QCameraFrameWidget::mouseReleaseEvent(QMouseEvent *event)
{
    qDebug() << __FUNCTION__;

    if (event->button() == Qt::LeftButton)
    {
        if (m_mode == EditEditAlert)
        {
            if (m_bDragPoint)
            {
                if (m_nDragIndex >= 0 && m_nDragIndex < (int)m_new_alert.m_points.size())
                {
                    auto p = widget2rel(event->pos());
                    m_new_alert.m_points[m_nDragIndex] = p;
                    processFrame(m_lastFrame);
                    emit require_confirm();
                }
            }
        }
    }
}

void QCameraFrameWidget::mouseMoveEvent(QMouseEvent * event)
{
    if (m_bDragPoint && (event->buttons() & Qt::LeftButton) == 0)
    {
        m_bDragPoint = false;
    }

    if (m_mode == EditNewAlert)
    {
        if (m_new_alert.m_points.size() >= 2)
        {
            auto p = widget2rel(event->pos());
            m_new_alert.m_points.back() = p;
            processFrame(m_lastFrame);
        }
    }

    if (m_mode == EditEditAlert)
    {
        if (m_bDragPoint)
        {
            if (m_nDragIndex >= 0 && m_nDragIndex < (int)m_new_alert.m_points.size())
            {
                auto p = widget2rel(event->pos());
                m_new_alert.m_points[m_nDragIndex] = p;
                processFrame(m_lastFrame);
            }
        }
    }
}

void QCameraFrameWidget::confirm_new_alert()
{
    qDebug() << __FUNCTION__;

    if (m_pCamera)
    {
        m_pCamera->m_alerts.push_back(m_new_alert);
        m_new_alert.reset();

        m_mode = EditNone;
        processFrame(m_lastFrame);
    }
}
