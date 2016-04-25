TEMPLATE = app
CONFIG += c++11
QT += widgets

DEFINES += QMAKE_PWD=\\\"$$PWD\\\"
DEFINES += QMAKE_OUT_PWD=\\\"$$OUT_PWD\\\"
DEFINES += QMAKE_QMAKE_QMAKE=\\\"$$QMAKE_QMAKE\\\"
DEFINES += QMAKE_QMAKESPEC=\\\"$$QMAKESPEC\\\"

RESOURCES += resources.qrc

SOURCES += \
    main.cpp \
    MainWindow.cpp \
    TestRunner.cpp \
    DirUtils.cpp \
    DirTestItem.cpp \
    FileTestItem.cpp \
    TestItem.cpp \
    TestTreeModel.cpp \
    TestTreeView.cpp \
    OutputWidget.cpp

HEADERS += \
    MainWindow.h \
    TestRunner.h \
    DirUtils.h \
    DirTestItem.h \
    FileTestItem.h \
    TestItem.h \
    TestTreeModel.h \
    TestTreeView.h \
    OutputWidget.h

