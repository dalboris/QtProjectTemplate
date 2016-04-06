#include <Test/Test.h>

#include <QCoreApplication>
#include <QApplication>

namespace Test
{

int runTestsCommon_(int argc, char *argv[])
{
    QCoreApplication::setAttribute(Qt::AA_Use96Dpi, true);
    QTEST_SET_MAIN_SOURCE_PATH

    bool fail = false;
    foreach(QObject * test, testList())
    {
        fail = fail || QTest::qExec(test, argc, argv);
    }

    return fail;
}

int runTests(int argc, char *argv[])
{
    QCoreApplication app(argc, argv);
    return runTestsCommon_(argc, argv);
}

int runGuiTests(int argc, char *argv[])
{
    QApplication app(argc, argv);
    return runTestsCommon_(argc, argv);
}

} // end namespace Test
