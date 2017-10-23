#ifndef CVVIDEOCAPURE_H
#define CVVIDEOCAPURE_H

#include <functional>
#include <opencv2/highgui/highgui.hpp>
#include <QString>
#include <QThread>
#include <QMutex>

Q_DECLARE_METATYPE(cv::Mat)

class QCvVideoCapure : public QThread
{
    Q_OBJECT

public:

    QCvVideoCapure();
    ~QCvVideoCapure();

    void start(QString const & strUrl, std::function<void(cv::Mat &&)> on_frame);
    void stop();

    cv::Mat get_frame()
    {
        QMutexLocker l(&m_queueMutex);
        return std::move(m_lastFrame);
    }

signals:

    void connected(bool bOk);
    void frameCaptured();

private slots:

    void processFrame(cv::Mat frame);

protected:

    void run();

private:

    QString          m_strUrl;
    cv::VideoCapture m_cap;
    volatile bool m_bStop;

    std::function<void(cv::Mat &&)> m_on_frame;

    QMutex  m_queueMutex;
    cv::Mat m_lastFrame;
};

#endif // CVVIDEOCAPURE_H
