TEMPLATE = lib
QT -= core gui

DEPENDS = \
    Geometry

HEADERS += \
    Foo.h

SOURCES += \
    Foo.cpp

include($$OUT_PWD/.config.pri)
