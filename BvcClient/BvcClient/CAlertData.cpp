#include "CAlertData.hpp"

#include <QJsonArray>

namespace BVC {

CAlertData::CAlertData()
{

}

CAlertData::CAlertData(QJsonObject const &json)
{
    if (json.contains("id"))
    {
        m_id = json["id"].toString();
    }

    auto t = json["type"].toString();

    if (t == "LD")
        m_type = AlertType::LoiteringDetection;
    else if (t == "RA")
        m_type = AlertType::RestrictedArea;
    else if (t == "VW")
        m_type = AlertType::VirtualWall;
    else
    {
        m_type = AlertType::None;
        return;
    }

    m_direction = BVC::AlertDirection::Both;

    if (json.contains("direction"))
    {
        auto dir = json["direction"].toString();
        if (dir == "L")
            m_direction = BVC::AlertDirection::ToLeft;
        else if (dir == "R")
            m_direction = BVC::AlertDirection::ToRight;
    }
    else if (m_type == AlertType::VirtualWall)
    {
        throw std::invalid_argument(__FUNCTION__);
    }

    m_duration = 0;

    if (json.contains("duration"))
    {
        m_duration = json["duration"].toInt();
        if (m_duration < 0)
            m_duration = 0;
    }
    else if (m_type == AlertType::LoiteringDetection)
    {
        throw std::invalid_argument(__FUNCTION__);
    }

    if (json.contains("points"))
    {
        auto && j_points = json["points"].toArray();

        for (auto && x : j_points)
        {
            auto && j_p = x.toArray();
            m_points.push_back({ (float)j_p[0].toDouble(), (float)j_p[1].toDouble() });
        }

        if (m_type == AlertType::VirtualWall && m_points.size() < 2)
            throw std::invalid_argument(__FUNCTION__);
    }
    else
    {
        throw std::invalid_argument(__FUNCTION__);
    }
}

CAlertData::operator QJsonObject() const
{
    QJsonObject j;

    if (!m_id.isEmpty())
        j["id"] = m_id;

    switch (m_type)
    {
    case AlertType::LoiteringDetection:
        j["type"] = "LD";
        j["duration"] = m_duration;
        break;

    case AlertType::RestrictedArea:
        j["type"] = "RA";
        break;

    case AlertType::VirtualWall:
        j["type"] = "VW";
        switch (m_direction)
        {
        case AlertDirection::Both:
            j["direction"] = "B";
            break;
        case AlertDirection::ToLeft:
            j["direction"] = "L";
            break;
        case AlertDirection::ToRight:
            j["direction"] = "R";
            break;
        }
        break;

    default:
        return {};
    }

    QJsonArray jps;
    for (auto & p : m_points)
    {
        QJsonArray jp;
        jp.append((double)p.x);
        jp.append((double)p.y);
        jps.append(jp);
    }

    j["points"] = jps;

    return j;
}

void CAlertData::set_id(QJsonObject const &json)
{
    if (json.contains("alert"))
    {
        m_id = json["alert"].toObject()["id"].toString();
    }
    else
    {
        m_id = json["id"].toString();
    }
}

} // namespace BVC
