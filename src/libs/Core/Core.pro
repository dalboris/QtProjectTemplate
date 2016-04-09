TEMPLATE = lib
CONFIG -= qt

DEPENDS = \
    Geometry

HEADERS += \
    Foo.h \
    Bar.h

SOURCES += \
    Foo.cpp \
    Bar.cpp

include($$OUT_PWD/.config.pri)
