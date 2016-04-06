
TEMPLATE = app
CONFIG += testcase
QT -= core gui
QT += testlib

DEPENDS = \
    Test \
    Core

HEADERS += \
    TestFoo.h

SOURCES += \
    main.cpp \
    TestFoo.cpp

include($$OUT_PWD/AutoBuild.pri)
