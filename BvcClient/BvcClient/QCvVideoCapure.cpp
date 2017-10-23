#include "QCvVideoCapure.h"
#include <QDebug>

QCvVideoCapure::QCvVideoCapure()
{
    qRegisterMetaType<cv::Mat>("cv_Mat");

    m_bStop = true;
}

QCvVideoCapure::~QCvVideoCapure()
{
    stop();
}

void QCvVideoCapure::start(QString const & strUrl, std::function<void(cv::Mat &&)> on_frame)
{
    qDebug() << __FUNCTION__ << ", url: " << strUrl;

    stop();

    m_strUrl = strUrl;
    m_on_frame = std::move(on_frame);
    m_lastFrame.release();

    m_bStop = false;
    QThread::start(LowPriority);
}

void QCvVideoCapure::stop()
{
    qDebug() << __FUNCTION__;

    if (isRunning())
    {
        m_bStop = true;
        wait();
    }
}

void QCvVideoCapure::run()
{
    qDebug() << __FUNCTION__ << " start";

    //m_cap.set(CV_CAP_PROP_BUFFERSIZE, 5);

    m_cap.open(m_strUrl.toStdString());

    if (!m_cap.isOpened())
    {
        qDebug() << __FUNCTION__ << " connection failed";
        QMetaObject::invokeMethod( this, "connected", Qt::QueuedConnection, Q_ARG(bool, false));
        return;
    }

    qDebug() << __FUNCTION__ << " connection ok";
    QMetaObject::invokeMethod( this, "connected", Qt::QueuedConnection, Q_ARG(bool, true));

    int delay = (1000000/m_cap.get(CV_CAP_PROP_FPS));

    if (delay < 100)
        delay = 100; // ns

    while (!m_bStop && m_cap.isOpened())
    {
        cv::Mat frame;

        if (!m_cap.read(frame))
            break;

        if (m_on_frame)
        {
            m_on_frame(std::move(frame));
        }
        else
        {
            QMutexLocker l(&m_queueMutex);
            m_lastFrame = std::move(frame);
            QMetaObject::invokeMethod( this, "frameCaptured", Qt::QueuedConnection);
            //QMetaObject::invokeMethod( this, "processFrame", Qt::QueuedConnection, Q_ARG(cv::Mat, std::move(frame)));
        }

        //usleep(delay);
    }

    qDebug() << __FUNCTION__ << " exit";
}

void QCvVideoCapure::processFrame(cv::Mat frame)
{
    QMutexLocker l(&m_queueMutex);
    m_lastFrame = std::move(frame);

    QMetaObject::invokeMethod( this, "frameCaptured", Qt::QueuedConnection );
}
