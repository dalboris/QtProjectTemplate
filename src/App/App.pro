TEMPLATE = app
CONFIG += qt
QT += widgets

DEPENDS = \
    Gui

SOURCES += main.cpp

include($$OUT_PWD/.config.pri)
