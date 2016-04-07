TEMPLATE = lib
QT += widgets

DEPENDS = \
    Gui/Widgets

HEADERS += \
    MainWindow.h

SOURCES += \
    MainWindow.cpp

include($$OUT_PWD/.config.pri)
