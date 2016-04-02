
include($$OUT_PWD/__gen__.pri)

###############################################################################
#                        XXX TODO: THINGS TO AUTOMATE
#

# Include headers from App1
APP1_SRC = $$PWD/..
INCLUDEPATH += $$APP1_SRC/
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$APP1_SRC/

# Lib1 directories
LIB1_SRC       = $$PWD/..
LIB1_OUT_UNIX  = $$OUT_PWD/..
LIB1_OUT_WIN32 = $$OUT_PWD/../$$RELEASE_OR_DEBUG # XXX double-check on Windows

# Include headers from Lib1
INCLUDEPATH += $$LIB1_SRC/
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$LIB1_SRC/

# Link to Lib1
unix:  LIBS += -L$$LIB1_OUT_UNIX/Lib1/ -lLib1
win32: LIBS += -L$$LIB1_OUT_WIN32/ # XXX double-check on Windows

#
#
###############################################################################

TEMPLATE = app
TARGET = App1
CONFIG += qt c++11
QT += widgets

# Variable to be parsed by build.py to handle dependencies
DEPENDS = \
    Lib1

HEADERS += \
    MainWindow.h

SOURCES += \
    main.cpp \
    MainWindow.cpp
