
TEMPLATE = app
CONFIG += testcase
QT -= core gui
QT += testlib

DEPENDS = \
    Core

SOURCES += \
    main.cpp

include($$OUT_PWD/AutoBuild.pri)
