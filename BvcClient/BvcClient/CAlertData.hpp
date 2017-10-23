#ifndef CALERTDATA_H
#define CALERTDATA_H

#include <opencv2/core.hpp>
#include <QJsonObject>

namespace BVC {

enum class AlertType
{
    None,
    LoiteringDetection,
    VirtualWall,
    RestrictedArea
};

enum class AlertDirection
{
    Both,
    ToLeft,
    ToRight,
};

class CAlertData
{
public:

    CAlertData();
    CAlertData(QJsonObject const &json);

    void set_id(QJsonObject const &json);

    void reset()
    {
        m_id.clear();
        m_type = AlertType::None;
        m_points.clear();
        m_direction = AlertDirection::Both;
        m_duration = 0;
    }

    operator QJsonObject() const;

public:

    QString         m_id;
    AlertType       m_type;
    std::vector<cv::Point2f>    m_points;
    AlertDirection  m_direction; // used for VirtualWall only
    int             m_duration; // time of seconds, used for LoiteringDetection only

};

} // namespace BVC

#endif // CALERTDATA_H
