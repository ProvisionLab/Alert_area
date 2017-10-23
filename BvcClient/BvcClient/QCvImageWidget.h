#ifndef QCVIMAGEWIDGET_H
#define QCVIMAGEWIDGET_H

#include <QLabel>
#include <QMouseEvent>
#include <QPoint>
#include <QQueue>

#include <opencv2/highgui/highgui.hpp>

class QCvImageWidget : public QLabel
{
    Q_OBJECT

public:

    explicit QCvImageWidget(QWidget *parent = 0);

    cv::Mat const & getLastFrame() const
    {
        return m_lastFrame;
    }

signals:

    //void new_calibration();

public slots:

    void showFrame(cv::Mat frame);
    void resizeEvent(QResizeEvent *);

protected:

    void processFrame(const cv::Mat & frame);
    virtual void postProcessImage(QPixmap & img);

    cv::Point2f widget2rel(QPoint pt) const;
    QPoint rel2widget(cv::Point2f pt) const;

    cv::Point2f widget2frame(QPoint) const;
    cv::Point2f widget2frame(cv::Size frmSize, QPoint pt) const;
    QPoint frame2widget(cv::Point2f) const;
    QPoint frame2widget(cv::Size frmSize, cv::Point2f) const;

protected:

    cv::Size    m_frameSize{0,0};
    cv::Mat     m_lastFrame;
};


#endif // QCVIMAGEWIDGET_H
