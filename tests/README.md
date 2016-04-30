
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


# How to run tests?

Let's assume you compiled the distribution this way:

```shell
$ git clone https://github.com/dalboris/QtProjectTemplate.git QtProjectTemplate
$ mkdir build-QtProjectTemplate
$ cd build-QtProjectTemplate
$ qmake ../QtProjectTemplate
$ make
```
(note: `qmake` may have to be replaced by something like `/home/boris/Qt/5.5/gcc_64/bin/qmake` to specify which version of qmake, and therefore Qt, to use)

Then in the build directory, you will find an application called `runtests` in the `tests/runtests` folder. Just run `./runtests all` to compile and run all the tests:

```shell
$ cd tests/runtests
$ ./runtests all
```

Or you can run only the tests in a specific folder:

```shell
$ ./runtests unit/Core
```

Or you can run a specific test by its name (i.e., without the `.cpp` extension):

```shell
$ ./runtests unit/Core/tst_foo
```

Or finally, you can run it without argument, which will launch a Gui application to select graphically which tests
to run and see their outputs. 

```shell
$ ./runtests
```

When you click on the "run" button, the test is automatically re-compiled if its timestamp is newer than the last compilation. Therefore, you can leave the `runtests` Gui application open while writing tests. Just modify+save your unit test in Qt Creator (or whatever editor), then click the run button in runtests. As simple as that.


# What black magic happens under the hood?

For each tst_Foo.cpp file to run, runtests performs the following actions in the build directory:

  1. Generates the following test source files:
      - tst_Foo.gen.h    (defines a QObject with all test functions as private slots)
      - tst_Foo.gen.cpp  (defines a main() function calling qExec on the QObject)
      - tst_Foo.gen.pro  (defines a Qt test project linking to the appropriate libs)

  2. Calls qmake/make on tst_Foo.gen.pro, which generates the binary:
      - tst_Foo     (on Unix)
      - tst_Foo.exe (on Windows)

  3. Executes the binary test program, and report whether the tests passed or failed

During step 1., runtests parses the test file for "#include" preprocessor directives, and uses this information to automagically find which libraries this test depends on, and then adds the appropriate compiler flags to use these libraries.

Also, note that runtests "remembers" the qmake configuration that was used to compile it. At runtime, it uses the same configuration to compile test files. This ensures that the tests are compiled with the same build configuration as the tested libraries.

# How to run memory analyzers on tests?

On Linux, compile in Debug mode, then manually call valgrind on the tst_Foo
test program you want to analyze. In the future, it would be nice to 
integrate this feature directly in the runtests tool, but it is not a
priority for now.
