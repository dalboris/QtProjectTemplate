
include($$OUT_PWD/_.pri)

TEMPLATE = app
CONFIG += qt
QT += widgets

DEPENDS = \
    Lib1

HEADERS += \
    MainWindow.h

SOURCES += \
    main.cpp \
    MainWindow.cpp
