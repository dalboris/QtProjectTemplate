
include($$OUT_PWD/Build.pri)

CONFIG(release, debug|release): RELEASE_OR_DEBUG = release
CONFIG(debug,   debug|release): RELEASE_OR_DEBUG = debug

LIB1_SRC       = $$PWD/..
LIB1_OUT_UNIX  = $$OUT_PWD/..
LIB1_OUT_WIN32 = $$OUT_PWD/../$$RELEASE_OR_DEBUG

INCLUDEPATH += $$LIB1_SRC/
!win32: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$LIB1_SRC/

unix:  LIBS += -L$$LIB1_OUT_UNIX/Lib1/ -lLib1
win32: LIBS += -L$$LIB1_OUT_WIN32/

INCLUDEPATH += $$PWD/..

TEMPLATE = app
TARGET = App1
CONFIG += qt c++11
QT += widgets

HEADERS += \
    MainWindow.h

SOURCES += \
    main.cpp \
    MainWindow.cpp
