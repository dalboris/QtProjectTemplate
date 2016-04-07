#include <Gui/Widgets/Widget.h>

#include <Core/Foo.h>

#include <iostream>

namespace Gui
{

Widget::Widget()
{
    std::cout << "Widget::Widget()" << std::endl;
    connect(this, &QPushButton::clicked, this, &Widget::onClick_);
}

void Widget::onClick_()
{
    std::cout << "Widget::onClick_()" << std::endl;
    Core::Foo foo;
    setText(QString().setNum(foo.return42()));
}

} // namespace Gui
