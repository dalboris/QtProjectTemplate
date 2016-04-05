
TEMPLATE = app
QT -= core gui
QT += testlib
CONFIG += testcase

DEPENDS = \
    Gui

SOURCES += \
    main.cpp

include($$OUT_PWD/AutoBuild.pri)
