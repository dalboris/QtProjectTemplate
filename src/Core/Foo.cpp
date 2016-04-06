#include <Core/Foo.h>

#include <iostream>

namespace Core
{

Foo::Foo()
{
    std::cout << "Foo::Foo()" << std::endl;
}

int Foo::return42()
{
    return 42;
}

} // end namespace Core
