#include <CoreTest.h>
#include <Core/Foo.h>

class Core_Foo: public QObject
{
    Q_OBJECT

private slots:

    void dummyTest()
    {
        Core::Foo foo;
    }
};
