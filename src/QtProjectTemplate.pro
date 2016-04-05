
# Execute AutoBuild.py script. This automatically generates one AutoBuild.pri
# file for each project in the distribution.
DISTFILES += AutoBuild.py
win32: PYTHON=python.exe
else:  PYTHON=python
system($$PYTHON AutoBuild.py $$PWD $$OUT_PWD)

# Subdir template. Note: no need to specify dependencies here. Appropriate
# dependency statements will be automatically added to AutoBuild.pri based on
# the value of DEPENDS in subprojects.
TEMPLATE = subdirs
SUBDIRS = \
    App \
    Gui

# Include AutoBuild.pri.
include($$OUT_PWD/AutoBuild.pri)

# XXX TODO: THINGS TO AUTOMATE
App.depends = Gui

