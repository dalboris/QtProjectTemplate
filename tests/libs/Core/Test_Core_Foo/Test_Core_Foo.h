
#include <CoreTest.h>
#include <Core/Foo.h>

class Test_Core_Foo: public QObject
{
    Q_OBJECT

private slots:

    void test() // <- rename test function
    {
        // ... test things here ...
    }

    // ... create other test functions here ...
};
