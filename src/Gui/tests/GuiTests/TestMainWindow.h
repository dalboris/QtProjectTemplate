#ifndef TESTMAINWINDOW_H
#define TESTMAINWINDOW_H

#include <Test/Test.h>

class TestMainWindow: public QObject
{
    Q_OBJECT

private slots:
    void testConstructor();
};

TEST_REGISTER(TestMainWindow)

#endif // TESTMAINWINDOW_H
