#ifndef TESTSTREEWIDGET_H
#define TESTSTREEWIDGET_H

#include <QTreeWidget>
#include <QDir>

class TestsTreeWidget : public QTreeWidget
{
public:
    TestsTreeWidget(const QDir & dir,
                    const QDir & outDir,
                    QWidget * parent = nullptr);

private:
    QDir dir_;
    QDir outDir_;
};

#endif // TESTSTREEWIDGET_H
