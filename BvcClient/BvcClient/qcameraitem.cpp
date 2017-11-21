#include "QCameraItem.h"
#include <QDebug>

QCameraItem::QCameraItem(QString const & name)
    : QListWidgetItem(name)
{

}

QString QCameraItem::get_url(QString username, QString password) const
{
    return m_Url;
/*
    if (username.isEmpty() || password.isEmpty())
        return m_Url;

    QUrl url(m_Url);

    qDebug() << "camera username: " << url.userName() << ", password: " << url.password();

    if (!url.userName().isEmpty())
        return m_Url;

    url.setUserName(username);
    url.setPassword(password);

    return url.toString();
*/
}

QCameraItem::QCameraItem(QJsonObject const & json)
    : QListWidgetItem(json["name"].toString())
{
    m_Id = json["id"].toInt();
    if (json.contains("rtspUrl"))
        m_Url = json["rtspUrl"].toString();
    else
        m_Url = json["url"].toString();

    if (json.contains("enabled"))
        m_enabled = json["enabled"].toBool();
    else
        m_enabled = true;


    //
    setFlags(flags() | Qt::ItemIsUserCheckable);
    setCheckState(m_enabled ? Qt::Checked : Qt::Unchecked);
}

void QCameraItem::update_state(QJsonObject const & json)
{
    if (json.contains("enabled"))
        m_enabled = json["enabled"].toBool();
    else
        m_enabled = true;

    setCheckState(m_enabled ? Qt::Checked : Qt::Unchecked);
}

QCameraItem::operator QJsonObject() const
{
    QJsonObject j_camera;

    j_camera["id"] = m_Id;
    j_camera["name"] = text();
    j_camera["url"] = m_Url;
    j_camera["enabled"] = m_enabled;

    return j_camera;
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
