#include "MainWindow.h"

#include <Lib1/Foo.h>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
{
    setWindowTitle("App1");

    Foo foo;
}

MainWindow::~MainWindow()
{

}
