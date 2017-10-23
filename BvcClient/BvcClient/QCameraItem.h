#ifndef QCAMERAITEM_H
#define QCAMERAITEM_H

#include <QListWidgetItem>
#include <QJsonObject>
#include <QJsonArray>
#include "CAlertData.hpp"
#include <vector>

class QCameraItem : public QListWidgetItem
{
public:

    QCameraItem(QString const & name);
    QCameraItem(QJsonObject const & json);

    void set_alerts(QJsonArray const & json);
    void del_alert(QString alert_id);
    void update_alert(BVC::CAlertData const & alert);

    QString get_url() const
    {
        if (m_username.isEmpty())
            return m_Url;

        QString protoName = "rtsp://";

        if (m_Url.size() < protoName.size())
            return {};

        if ( m_Url.left(protoName.size()) == protoName )
        {
            return QString("%1%2:%3@%4")
                    .arg(protoName)
                    .arg(m_username)
                    .arg(m_password)
                    .arg(m_Url.right(m_Url.size()- protoName.size()));
        }

        return {};
    }

public:

    QString m_Id;
    QString m_Url;
    QString m_username;
    QString m_password;

    std::vector<BVC::CAlertData>    m_alerts;
};

class QCameraAlertItem : public QListWidgetItem
{
public:

    QCameraAlertItem(QCameraItem * camera, QString const & id, QString const & name);

public:

    QCameraItem * m_camera;
    QString m_id;
};

#endif // QCAMERAITEM_H
