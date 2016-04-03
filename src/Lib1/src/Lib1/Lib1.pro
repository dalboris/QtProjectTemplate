
###############################################################################
#                        XXX TODO: THINGS TO AUTOMATE
#

INCLUDEPATH += $$PWD/..
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$PWD/..

#
#
###############################################################################

TEMPLATE = lib
CONFIG += staticlib
QT -= core gui

HEADERS += \
    Foo.h

SOURCES += \
    Foo.cpp
