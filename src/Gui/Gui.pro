TEMPLATE = lib
QT += widgets

DEPENDS = \
    Core

HEADERS += \
    MainWindow.h

SOURCES += \
    MainWindow.cpp

include($$OUT_PWD/.config.pri)
