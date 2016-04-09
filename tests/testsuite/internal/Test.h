
#ifndef TEST_H
#define TEST_H

#include <QtTest/QtTest>
#include <QObject>

// Note: AppType must be predefined in the file including this header.
//       It must be either QApplication or QCoreApplication.

#define TEST_DEFINE_MAIN(TestType) \
    int main(int argc, char *argv[]) \
    { \
        AppType app(argc, argv); \
        QCoreApplication::setAttribute(Qt::AA_Use96Dpi, true); \
        QTEST_SET_MAIN_SOURCE_PATH \
        TestType test; \
        return QTest::qExec(&test, argc, argv); \
    }

#endif // TEST_H
