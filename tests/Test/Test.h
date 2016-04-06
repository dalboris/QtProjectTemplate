#ifndef TEST_TEST_H
#define TEST_TEST_H

#include <QtTest/QtTest>
#include <QObject>
#include <QList>

#define TEST_REGISTER(TestObject) \
    static Test::RegisterTest<TestObject> TestObject##Instance;

namespace Test
{

inline QList<QObject*> & testList()
{
    static QList<QObject*> list;
    return list;
}

inline void addTest(QObject * object)
{
    QList<QObject*> & list = testList();
    if (!list.contains(object))
    {
        list.append(object);
    }
}

template <class TestObject>
class RegisterTest
{
public:
    RegisterTest()
    {
        addTest(testObject());
    }

    inline TestObject * testObject()
    {
        static TestObject to;
        return &to;
    }
};

int runTests(int argc, char *argv[]);
int runGuiTests(int argc, char *argv[]);

} // end namespace Test

#endif // TEST_TEST_H
