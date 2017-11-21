#ifndef QCAMERAITEM_H
#define QCAMERAITEM_H

#include <QListWidgetItem>
#include <QJsonObject>
#include <QJsonArray>
#include <QUrl>
#include "CAlertData.hpp"
#include <vector>

class QCameraItem : public QListWidgetItem
{
public:

    QCameraItem(QString const & name);
    QCameraItem(QJsonObject const & json);

    operator QJsonObject() const;

    void set_alerts(QJsonArray const & json);
    void del_alert(QString alert_id);
    void update_alert(BVC::CAlertData const & alert);

    QString get_url(QString username, QString password) const;

public:

    int m_Id;
    QString m_Url;
    bool m_enabled;

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
