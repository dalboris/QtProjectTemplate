TEMPLATE = lib
CONFIG -= qt

THIRD_DEPENDS = \
    Geometry

HEADERS += \
    Foo.h \
    Bar.h

SOURCES += \
    Foo.cpp \
    Bar.cpp

include($$OUT_PWD/.config.pri)
