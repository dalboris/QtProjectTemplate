#include <Core/Foo.h>
#include <Geometry/Point.h>
#include <iostream>

namespace Core
{

Foo::Foo()
{
    std::cout << "Foo::Foo()" << std::endl;
    Geometry::Point point;
}

int Foo::return42()
{
    return 42;
}

} // end namespace Core
