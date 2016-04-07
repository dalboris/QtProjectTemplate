#ifndef GUI_WIDGET_H
#define GUI_WIDGET_H

#include <QPushButton>

namespace Gui
{

class Widget: public QPushButton
{
    Q_OBJECT

public:
    Widget();

private slots:
    void onClick_();
};

} // namespace Gui

#endif // GUI_WIDGET_H
