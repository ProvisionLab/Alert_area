#include "QCvImageWidget.h"
#include <QLayout>
#include <QDebug>

#include <opencv2/core/core.hpp>
#include <opencv2/imgproc/imgproc.hpp>

QCvImageWidget::QCvImageWidget(QWidget *parent)
    : QLabel(parent)
{
    setAlignment(Qt::AlignTop|Qt::AlignLeft);
    //setAlignment(Qt::AlignCenter);
    //setAlignment(Qt::AlignBottom|Qt::AlignRight);
}


void QCvImageWidget::postProcessImage(QPixmap &)
{
}

void QCvImageWidget::processFrame(const cv::Mat & frame)
{
    QImage img;

    if (frame.channels() == 3)
    {
        cv::Mat RGBframe;
        cv::cvtColor(frame, RGBframe, CV_BGR2RGB);
        img = QImage((const unsigned char *)RGBframe.data, RGBframe.cols, RGBframe.rows, static_cast<int>(RGBframe.step), QImage::Format_RGB888);
        img.bits();
    }
    else
    {
        img = QImage((const unsigned char *)frame.data, frame.cols, frame.rows, static_cast<int>(frame.step), QImage::Format_Grayscale8);
        img.bits();
    }

    if (!img.isNull())
    {
        auto pm = QPixmap::fromImage(img)
                .scaled(size(), Qt::KeepAspectRatio, Qt::FastTransformation);

        postProcessImage(pm);

        // show image

        setPixmap(std::move(pm));
    }
}

void QCvImageWidget::resizeEvent(QResizeEvent *)
{
    //qDebug() << __FUNCTION__;
}

void QCvImageWidget::showFrame(cv::Mat frame)
{
    m_frameSize = frame.size();
    m_lastFrame = std::move(frame);

    processFrame(m_lastFrame);
}

cv::Point2f QCvImageWidget::widget2rel(QPoint pt) const
{
    if (!pixmap())
        return {0,0};

    auto wgSize = size();
    auto pmSize = pixmap()->size();
    if (pmSize.isEmpty())
        return {0,0};

    int px = pt.x();
    int py = pt.y();

    auto al = alignment();

    if (al & Qt::AlignHCenter)
        px -= (wgSize.width() - pmSize.width())/2;
    else if (al & Qt::AlignRight)
        px -= (wgSize.width() - pmSize.width());

    if (al & Qt::AlignVCenter)
        py -= (wgSize.height() - pmSize.height())/2;
    else if (al & Qt::AlignBottom)
        py -= (wgSize.height() - pmSize.height());

    float x = (float)px / (float)pmSize.width();
    float y = (float)py / (float)pmSize.height();

    return cv::Point2f(x, y);
}

QPoint QCvImageWidget::rel2widget(cv::Point2f pt) const
{
    QSize pmSize = pixmap() ? pixmap()->size() : QSize{0,0};

    int px = pt.x * pmSize.width();
    int py = pt.y * pmSize.height();

    auto wgSize = size();
    auto al = alignment();

    if (al & Qt::AlignHCenter)
       px += (wgSize.width() - pmSize.width())/2;
    else if (al & Qt::AlignRight)
       px += (wgSize.width() - pmSize.width());

    if (al & Qt::AlignVCenter)
       py += (wgSize.height() - pmSize.height())/2;
    else if (al & Qt::AlignBottom)
       py += (wgSize.height() - pmSize.height());

    return {px, py};
}

QPoint QCvImageWidget::frame2widget(cv::Size frmSize, cv::Point2f pt) const
{
    if (frmSize.width <= 0 || frmSize.height <= 0)
        return {0,0};

    if (!pixmap())
        return {0,0};

    auto wgSize = size();
    auto pmSize = pixmap()->size();

    int px = (pt.x * pmSize.width())/frmSize.width;
    int py = (pt.y * pmSize.height())/frmSize.height;

    auto al = alignment();

    if (al & Qt::AlignHCenter)
       px += (wgSize.width() - pmSize.width())/2;
    else if (al & Qt::AlignRight)
       px += (wgSize.width() - pmSize.width());

    if (al & Qt::AlignVCenter)
        py += (wgSize.height() - pmSize.height())/2;
    else if (al & Qt::AlignBottom)
        py += (wgSize.height() - pmSize.height());

    return {px, py};
}

QPoint QCvImageWidget::frame2widget(cv::Point2f pt) const
{
    return frame2widget(m_frameSize, pt);
}

cv::Point2f QCvImageWidget::widget2frame(cv::Size frmSize, QPoint pt) const
{
    if (!pixmap())
        return {0,0};

    auto wgSize = size();
    auto pmSize = pixmap()->size();
    if (pmSize.isEmpty())
        return {0,0};

    int px = pt.x();
    int py = pt.y();

    auto al = alignment();

    if (al & Qt::AlignHCenter)
        px -= (wgSize.width() - pmSize.width())/2;
    else if (al & Qt::AlignRight)
        px -= (wgSize.width() - pmSize.width());

    if (al & Qt::AlignVCenter)
        py -= (wgSize.height() - pmSize.height())/2;
    else if (al & Qt::AlignBottom)
        py -= (wgSize.height() - pmSize.height());

    float x = (px * frmSize.width) / pmSize.width();
    float y = (py * frmSize.height) / pmSize.height();

    return cv::Point2f(x, y);
}

cv::Point2f QCvImageWidget::widget2frame(QPoint pt) const
{
    return widget2frame(m_frameSize, pt);
}
