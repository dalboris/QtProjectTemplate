TEMPLATE = app
CONFIG += qt
QT += widgets

DEPENDS = \
    Gui/Windows

SOURCES += main.cpp

include($$OUT_PWD/.config.pri)
