
include($$OUT_PWD/_.pri)

###############################################################################
#                        XXX TODO: THINGS TO AUTOMATE
#

# Root src/ directory (i.e., parent dir of the outermost .pro file)
ROOT_PWD     =  $$PWD/../../..
ROOT_OUT_PWD =  $$OUT_PWD/../../..

# Add App1 to INCLUDEPATH
APP1_INCLUDE = $$PWD/..
INCLUDEPATH += $$APP1_INCLUDE/
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$APP1_INCLUDE/

# Add Lib1 to INCLUDEPATH (i.e., fix "cannot find Lib1/Foo.h" compile errors)
LIB1_INCLUDE = $$ROOT_PWD/Lib1/src
INCLUDEPATH += $$LIB1_INCLUDE/
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$LIB1_INCLUDE/

# Add Lib1 to LIBS (i.e., fix "undefined reference to `Foo::Foo()'" linking errors)
LIB1_LIB = $$ROOT_OUT_PWD/Lib1/src/Lib1
unix:  LIBS += -L$$LIB1_LIB/ -lLib1
win32: LIBS += -L$$LIB1_LIB_WIN32/RELEASE_OR_DEBUG # XXX double-check on Windows

#
#
###############################################################################

TEMPLATE = app
CONFIG += qt
QT += widgets

# Variable to be parsed by build.py to handle dependencies
DEPENDS = \
    Lib1

HEADERS += \
    MainWindow.h

SOURCES += \
    main.cpp \
    MainWindow.cpp
