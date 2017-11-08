#ifndef CBECONNECTION_H
#define CBECONNECTION_H

#include <QtNetwork/QNetworkAccessManager>
#include <functional>
#include <memory>

namespace BVC {

class CConnection
{
public:

    CConnection();

    void Open();


    void auth(QString url, QString username, QString password, std::function<void(bool succeeded)> callback);

    void get_cameras(std::function<void(QJsonObject const&)> callback);
    void get_camera_alerts(int camera_id, std::function<void(QJsonObject const&)> callback);

    void post_camera_alert(int camera_id, QJsonObject const & j_alert, std::function<void(QJsonObject const&)> callback);

    void delete_camera_alert(int camera_id, QString alert_id, std::function<void(QJsonObject const&)> callback);
    void update_camera_alert(int camera_id, QString alert_id, QJsonObject const & j_alert, std::function<void(QJsonObject const&)> callback);

protected:

    QNetworkAccessManager   m_nm;
    QString     m_apiUrl;
    QString     m_username;
    QString     m_password;
    QString     m_access_token;
};

} // namespace BVC



#endif // CBECONNECTION_H
