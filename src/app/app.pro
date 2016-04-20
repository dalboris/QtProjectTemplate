TEMPLATE = app
CONFIG += qt
QT += widgets

LIB_DEPENDS = \
    Gui/Windows

SOURCES += main.cpp

include($$OUT_PWD/.config.pri)
