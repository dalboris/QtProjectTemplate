#include "TestFoo.h"

#include <Core/Foo.h>

void TestFoo::testReturn42()
{
    Core::Foo foo;
    QCOMPARE(foo.return42(), 42);
}
