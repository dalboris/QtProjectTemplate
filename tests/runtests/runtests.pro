TEMPLATE = app
CONFIG += c++11
QT += widgets

DEFINES += QMAKE_PWD=\\\"$$PWD\\\"
DEFINES += QMAKE_OUT_PWD=\\\"$$OUT_PWD\\\"
DEFINES += QMAKE_QMAKE_QMAKE=\\\"$$QMAKE_QMAKE\\\"
DEFINES += QMAKE_QMAKESPEC=\\\"$$QMAKESPEC\\\"

SOURCES += \
    main.cpp \
    MainWindow.cpp \
    TestRunner.cpp \
    TestsTreeWidget.cpp

HEADERS += \
    MainWindow.h \
    TestRunner.h \
    TestsTreeWidget.h

