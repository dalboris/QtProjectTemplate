#include <Gui/MainWindow.h>

#include <Core/Foo.h>

#include <iostream>

namespace Gui
{

MainWindow::MainWindow()
{
    std::cout << "MainWindow::MainWindow()" << std::endl;

    Core::Foo foo;
}

} // namespace Gui
