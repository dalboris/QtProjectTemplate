
# How to write a unit test?

To write a unit test, simply create a file tst_Foo.cpp anywhere in the
tests/unit/ folder, following the following template:

```cpp
#include "Test.h"

BEGIN_TESTS

/* Write tests here */

END_TESTS
```

There should be one and only pair of BEGIN_TESTS/END_TESTS, and these keywords
must not appear anywhere else, including in comments.

Each test is a function with no parameters. Tests should be independent from
one another, i.e., they shouldn't call each others. Here is an example with
two test functions:

```cpp
#include "Test.h"
#include <MyLib/Foo.h>

BEGIN_TESTS

void makeAndDestroyFoo()
{
    MyLib::Foo fooOnTheStack;
    MyLib::Foo * fooOnTheHeap = new MyLib::Foo();
    delete fooOnTheHeap;
}

void return42()
{
    MyLib::Foo foo;
    QCOMPARE(foo.return42(), 42);
}

END_TESTS
```

Feel free to ease writing tests with `using namespace`:

```cpp
#include "Test.h"
#include <MyLib/Foo.h>
using namespace MyLib;

BEGIN_TESTS

void makeAndDestroyFoo()
{
    Foo fooOnTheStack;
    Foo * fooOnTheHeap = new Foo();
    delete fooOnTheHeap;
}

void return42()
{
    Foo foo;
    QCOMPARE(foo.return42(), 42);
}

END_TESTS
```

You must not declare any global objects. Though, you may declare any
convenient classes/functions before BEGIN_TESTS/END_TESTS that may
be shared between tests.

```cpp
#include "Test.h"
#include <MyLib/Foo.h>
using namespace MyLib;

struct FooPair { Foo foo1, foo2; }

Foo * makeFoo() { return new Foo(); }
void destroyFoo(Foo * foo) { delete foo; }

BEGIN_TESTS

void makeAndDestroyFoo()
{
    Foo fooOnTheStack;
    Foo * fooOnTheHeap = makeFoo();
    destroyFoo(fooOnTheHeap);
}

void return42()
{
    Foo * foo = makeFoo();
    FooPair p;
    QCOMPARE(foo->return42(), 42);
    QCOMPARE(p.foo1.return42(), 42);
    QCOMPARE(p.foo2.return42(), 42);
}

END_TESTS
```


# How to compile and run tests:

Just run the 'runtests' program, either interactively or with the command-line.

The command-line version takes one parameter: the path to the test file or the
test folder you want to compile and run. 

The interactive version is a Gui to let you graphically select which test
file or folder to compile and run

Either way, runtests will perform in the build directory the following actions,
on the selected tst_Foo.cpp file (or on all test files within the selected
test folder):

  1. Generate the following test source files:
      - tst_Foo.gen.h    (defines a QObject with all test functions as private slots)
      - tst_Foo.gen.cpp  (defines a main() function calling qExec on the QObject)
      - tst_Foo.gen.pro  (defines a Qt test project linking to the appropriate libs)

  2. Call qmake/make on tst_Foo.gen.pro, which will generate the binary:
      - tst_Foo     (on Unix)
      - tst_Foo.exe (on Windows)

  3. Execute the binary test program, and report whether the tests passed or failed


# How to run memory analyzers on tests?

On Linux, compile in Debug mode, then manually call valgrind on the tst_Foo
test program you want to analyze. In the future, it would be nice to be  able
do integrate this feature directly in the runtests tool, but it is not a
priority for now.
