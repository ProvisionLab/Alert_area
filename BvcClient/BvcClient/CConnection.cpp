#include "CConnection.h"
#include <QtNetwork/QNetworkRequest>
#include <QtNetwork/QNetworkReply>
#include <QJsonDocument>
#include <QJsonObject>
#include <QJsonArray>
#include <QDebug>
#include "auth_config.h"

#define BVC_USER_AGENT  "BVC ROGTool"

namespace BVC {

class RequestContext
{
public:

    RequestContext(QNetworkReply *reply)
        : m_reply(reply)
    {
//        QObject::connect(reply, &QNetworkReply::finished, [this]()
//        {
//        });

        QObject::connect(reply, &QNetworkReply::finished, [this]()
        {
            qDebug() << "QNetworkReply::finished";

            if (m_reply->error())
            {
                qDebug() << QString("http request failed: %1.").arg(m_reply->errorString());
            }
            else
            {
                qDebug() << "bytesAvailable: " << m_reply->bytesAvailable();
            }
        });

        QObject::connect(reply, &QIODevice::readyRead, [this]()
        {
            if (m_reply)
                data += m_reply->readAll();
        });

    }

public:

    QNetworkReply * m_reply;
    QByteArray data;
};

CConnection::CConnection()
{
    m_apiUrl = BVCAPI_URL;
    m_api_username = BVCAPI_USERNAME;
    m_api_password = BVCAPI_PASSWORD;

    m_nUserId = 0;
}

void CConnection::Open()
{

}

void CConnection::rog_auth(QString username, QString password, std::function<void(int user_id, QString auth_token)> callback)
{
    QNetworkRequest request(QString("%1/api/v1/sessions").arg(ROGAPI_URL));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

    QJsonObject j_session;
    j_session["email"] = username;
    j_session["password"] = password;

    QJsonObject j_auth;
    j_auth["session"] = j_session;

    QJsonDocument j_doc(j_auth);

    auto *reply = m_nm.post(request, j_doc.toJson());
    auto ctx = std::make_shared<RequestContext>(reply);

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        QString token;
        int user_id = 0;
        if (ctx->m_reply->error() != QNetworkReply::NoError)
        {
            qDebug() << "rog auth failed: " << ctx->m_reply->error();
        }
        else
        {
            QJsonDocument doc = QJsonDocument::fromJson(ctx->data);
            if (doc.isObject())
            {
                auto && j = doc.object();

                qDebug() << "rog auth reply: " << j;

                if (j.contains("jwt") && j.contains("user"))
                {
                    token = j["jwt"].toString();

                    auto && j_user = j["user"].toObject();
                    user_id = j_user["id"].toInt();
                }
                else
                {
                    qDebug() << "rog auth failed: no token";
                }
            }
            else
            {
                qDebug() << "rog auth failed: no json";
            }
        }

        callback(user_id, token);

        ctx->m_reply->deleteLater();
    });
}

void CConnection::rog_get_cameras(QString const & rog_token, std::function<void(QJsonObject const&)> callback)
{
    QNetworkRequest request(QString("%1/api/v1/me/cameras").arg(ROGAPI_URL));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setRawHeader("Authorization", rog_token.toLocal8Bit());

    auto ctx = std::make_shared<RequestContext>(
                    m_nm.get(request));

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        QJsonObject result;

        qDebug() << "rog get cameras status: " << ctx->m_reply->error();

        if (ctx->m_reply->error() == QNetworkReply::NoError)
        {
            QJsonDocument doc = QJsonDocument::fromJson(ctx->data);
            if (doc.isObject())
            {
                result = doc.object();
            }
        }

        callback(result);

        ctx->m_reply->deleteLater();
    });
}

void CConnection::auth(std::function<void(bool succeeded)> callback)
{
    QNetworkRequest request(QString("%1/api/auth").arg(m_apiUrl));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");

#if !BVCAPI_VERIFY_SSL
    QSslConfiguration conf = request.sslConfiguration();
    conf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(conf);
#endif

    QJsonObject j_auth;

    j_auth["username"] = m_api_username;
    j_auth["password"] = m_api_password;

    QJsonDocument j_doc(j_auth);

    auto *reply = m_nm.post(request, j_doc.toJson());
    auto ctx = std::make_shared<RequestContext>(reply);

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        QJsonDocument doc = QJsonDocument::fromJson(ctx->data);
        if (doc.isObject())
        {
            auto && j = doc.object();

            qDebug() << "auth reply: " << j;

            if (j.contains("access_token"))
            {
                m_access_token = j["access_token"].toString();
                callback(true);
            }
            else
            {
                m_access_token.clear();
                callback(false);
            }
        }
        else
        {
            callback(false);
        }

        ctx->m_reply->deleteLater();
    });
}

void CConnection::get_cameras(std::function<void(QJsonObject const&)> callback)
{
    QNetworkRequest request(QString("%1/api/user/%2/cameras")
                            .arg(m_apiUrl)
                            .arg(m_nUserId));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setRawHeader("Authorization", ("JWT " + m_access_token).toLocal8Bit());

#if !BVCAPI_VERIFY_SSL
    QSslConfiguration conf = request.sslConfiguration();
    conf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(conf);
#endif

    auto ctx = std::make_shared<RequestContext>(
                    m_nm.get(request));

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        if (ctx->m_reply->error() == QNetworkReply::AuthenticationRequiredError)
        {

        }

        QJsonDocument doc = QJsonDocument::fromJson(ctx->data);
        if (doc.isObject())
        {
            callback(doc.object());
        }

        ctx->m_reply->deleteLater();
    });
}

void CConnection::set_cameras(QJsonArray const j_cameras, std::function<void(bool succeeded)> callback)
{
    QNetworkRequest request(QString("%1/api/user/%2/cameras")
                            .arg(m_apiUrl)
                            .arg(m_nUserId));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", ("JWT " + m_access_token).toLocal8Bit());

#if !BVCAPI_VERIFY_SSL
    QSslConfiguration conf = request.sslConfiguration();
    conf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(conf);
#endif

    QJsonDocument j_doc(j_cameras);

    auto *reply = m_nm.put(request, j_doc.toJson());
    auto ctx = std::make_shared<RequestContext>(reply);

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        callback(ctx->m_reply->error() == QNetworkReply::NoError);

        ctx->m_reply->deleteLater();
    });

}

void CConnection::set_camera_enabled(int camera_id, bool enabled, std::function<void(bool succeeded)> callback)
{
    QNetworkRequest request(QString("%1/api/cameras/%2/enabled").arg(m_apiUrl).arg(camera_id));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", ("JWT " + m_access_token).toLocal8Bit());

#if !BVCAPI_VERIFY_SSL
    QSslConfiguration conf = request.sslConfiguration();
    conf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(conf);
#endif

    QJsonObject j_value;
    j_value["enabled"] = enabled;

    auto *reply = m_nm.put(request, QJsonDocument(j_value).toJson());
    auto ctx = std::make_shared<RequestContext>(reply);

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        callback(ctx->m_reply->error() == QNetworkReply::NoError);

        ctx->m_reply->deleteLater();
    });
}

void CConnection::get_camera_alerts(int camera_id, std::function<void(QJsonObject const&)> callback)
{
    QNetworkRequest request(QString("%1/api/cameras/%2/alerts").arg(m_apiUrl).arg(camera_id));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setRawHeader("Authorization", ("JWT " + m_access_token).toLocal8Bit());

#if !BVCAPI_VERIFY_SSL
    QSslConfiguration conf = request.sslConfiguration();
    conf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(conf);
#endif

    auto ctx = std::make_shared<RequestContext>(
                    m_nm.get(request));

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        QJsonDocument doc = QJsonDocument::fromJson(ctx->data);
        if (doc.isObject())
        {
            callback(doc.object());
        }

        ctx->m_reply->deleteLater();
    });
}

void CConnection::post_camera_alert(int camera_id, QJsonObject const & j_alert, std::function<void(QJsonObject const&)> callback)
{
    qDebug() << __FUNCTION__;

    QNetworkRequest request(QString("%1/api/cameras/%2/alerts").arg(m_apiUrl).arg(camera_id));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", ("JWT " + m_access_token).toLocal8Bit());

#if !BVCAPI_VERIFY_SSL
    QSslConfiguration conf = request.sslConfiguration();
    conf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(conf);
#endif

    QJsonDocument j_doc(j_alert);

    qDebug() << "post alert: " << j_alert;

    auto ctx = std::make_shared<RequestContext>(
                m_nm.post(request, j_doc.toJson()));

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        QJsonDocument doc = QJsonDocument::fromJson(ctx->data);
        if (doc.isObject())
        {
            callback(doc.object());
        }

        ctx->m_reply->deleteLater();
    });
}

void CConnection::delete_camera_alert(int camera_id, QString alert_id,
    std::function<void(QJsonObject const&)> callback)
{
    QNetworkRequest request(QString("%1/api/cameras/%2/alerts/%3")
                            .arg(m_apiUrl)
                            .arg(camera_id)
                            .arg(alert_id));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setRawHeader("Authorization", ("JWT " + m_access_token).toLocal8Bit());

#if !BVCAPI_VERIFY_SSL
    QSslConfiguration conf = request.sslConfiguration();
    conf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(conf);
#endif

    auto ctx = std::make_shared<RequestContext>(
                m_nm.deleteResource(request));

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        QJsonDocument doc = QJsonDocument::fromJson(ctx->data);
        if (doc.isObject())
        {
            callback(doc.object());
        }

        ctx->m_reply->deleteLater();
    });
}

void CConnection::update_camera_alert(int camera_id, QString alert_id, QJsonObject const & j_alert,
    std::function<void(QJsonObject const&)> callback)
{
    qDebug() << __FUNCTION__;

    QNetworkRequest request(QString("%1/api/cameras/%2/alerts/%3")
                            .arg(m_apiUrl)
                            .arg(camera_id)
                            .arg(alert_id));
    request.setHeader(QNetworkRequest::UserAgentHeader, BVC_USER_AGENT);
    request.setHeader(QNetworkRequest::ContentTypeHeader, "application/json");
    request.setRawHeader("Authorization", ("JWT " + m_access_token).toLocal8Bit());

#if !BVCAPI_VERIFY_SSL
    QSslConfiguration conf = request.sslConfiguration();
    conf.setPeerVerifyMode(QSslSocket::VerifyNone);
    request.setSslConfiguration(conf);
#endif

    qDebug() << "update alert: " << j_alert;

    QJsonDocument j_doc(j_alert);

    auto ctx = std::make_shared<RequestContext>(
        m_nm.put(request, j_doc.toJson()));

    QObject::connect(ctx->m_reply, &QNetworkReply::finished, [this, ctx, callback]()
    {
        QJsonDocument doc = QJsonDocument::fromJson(ctx->data);
        if (doc.isObject())
        {
            callback(doc.object());
        }

        ctx->m_reply->deleteLater();
    });
}


} // namespace BVC
