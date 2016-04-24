#include "TestsTreeWidgetItemWidget.h"

#include "TestRunner.h"

#include <QPushButton>
#include <QHBoxLayout>
#include <QLabel>

TestsTreeWidgetItemWidget::TestsTreeWidgetItemWidget(
        TestRunner * testRunner,
        QWidget * parent) :

    QWidget(parent),
    testRunner_(testRunner),
    subdirRunner_(nullptr)
{
    testRunner->setParent(this);

    QHBoxLayout * layout = new QHBoxLayout();
    layout->addWidget(new QPushButton("Compile"));
    layout->addWidget(new QPushButton("Run"));
    layout->addWidget(new QLabel(testRunner->testName()));
    setLayout(layout);
}
