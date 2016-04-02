
include($$OUT_PWD/__gen__.pri)

TEMPLATE = app
TARGET = App2
CONFIG += qt c++11
QT += widgets

HEADERS += \
    MainWindow.h

SOURCES += \
    main.cpp \
    MainWindow.cpp
