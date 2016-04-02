
include($$OUT_PWD/Build.pri)

TEMPLATE = app
TARGET = App2
CONFIG += qt c++11
QT += widgets

HEADERS += \
    MainWindow.h

SOURCES += \
    main.cpp \
    MainWindow.cpp
