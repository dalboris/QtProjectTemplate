#ifndef TESTFOO_H
#define TESTFOO_H

#include <Test/Test.h>

class TestFoo: public QObject
{
    Q_OBJECT

private slots:
    void testReturn42();
};

TEST_REGISTER(TestFoo)

#endif // TESTFOO_H
