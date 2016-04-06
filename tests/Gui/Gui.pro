
TEMPLATE = app
CONFIG += testcase
QT += widgets
QT += testlib

DEPENDS = \
    Test \
    Gui

HEADERS += \
    TestMainWindow.h

SOURCES += \
    main.cpp \
    TestMainWindow.cpp

include($$OUT_PWD/AutoBuild.pri)
