#ifndef TESTSTREEWIDGETITEMWIDGET_H
#define TESTSTREEWIDGETITEMWIDGET_H

#include <QWidget>

class TestRunner;
class SubdirRunner;

class TestsTreeWidgetItemWidget : public QWidget
{
    Q_OBJECT

public:
    // This TestsTreeWidgetItemWidget takes ownership of the test runner
    TestsTreeWidgetItemWidget(TestRunner * testRunner,
                              QWidget * parent = nullptr);

private:
    TestRunner * testRunner_;
    SubdirRunner * subdirRunner_;
};

#endif // TESTSTREEWIDGETITEMWIDGET_H
