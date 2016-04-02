
include($$OUT_PWD/__gen__.pri)

INCLUDEPATH += $$PWD/..
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$PWD/..

TEMPLATE = lib
TARGET = Lib1
CONFIG += staticlib c++11
QT -= core gui

HEADERS += \
    Foo.h

SOURCES += \
    Foo.cpp
