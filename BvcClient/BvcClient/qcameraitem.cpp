#include "QCameraItem.h"

QCameraItem::QCameraItem(QString const & name)
    : QListWidgetItem(name)
{

}

QCameraItem::QCameraItem(QJsonObject const & json)
    : QListWidgetItem(json["name"].toString())
    , m_Id(json["id"].toInt())
    , m_Url(json["url"].toString())
{
}

void QCameraItem::set_alerts(QJsonArray const & json)
{
    m_alerts.clear();

    for (auto && x : json)
    {
       if (x.isObject())
       {
            auto && j_alert = x.toObject();

            m_alerts.push_back(j_alert);
       }
    }
}

void QCameraItem::del_alert(QString alert_id)
{
    for (auto it = m_alerts.begin(); it != m_alerts.end(); ++it)
    {
       if (it->m_id == alert_id)
       {
           m_alerts.erase(it);
           break;
       }
    }
}

void QCameraItem::update_alert(BVC::CAlertData const & alert)
{
    for (auto it = m_alerts.begin(); it != m_alerts.end(); ++it)
    {
       if (it->m_id == alert.m_id)
       {
           *it = alert;
           break;
       }
    }
}

QCameraAlertItem::QCameraAlertItem(QCameraItem * camera, QString const & id, QString const & name)
    : QListWidgetItem(name)
    , m_camera(camera)
    , m_id(id)
{

}
