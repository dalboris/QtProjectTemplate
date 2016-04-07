#include <Gui/Windows/MainWindow.h>

#include <Gui/Widgets/Widget.h>
#include <Core/Foo.h>

#include <iostream>

namespace Gui
{

MainWindow::MainWindow()
{
    std::cout << "MainWindow::MainWindow()" << std::endl;
    setCentralWidget(new Gui::Widget());
}

} // namespace Gui
