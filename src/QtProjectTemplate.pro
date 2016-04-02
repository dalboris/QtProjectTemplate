
# Preliminary build step
DISTFILES += build.py
win32: PYTHON=python.exe
else:  PYTHON=python
system($$PYTHON build.py $$PWD $$OUT_PWD)

App1.depends = Lib1

# Subdirs
TEMPLATE = subdirs
SUBDIRS += \
    App2 \
    App1 \
    Lib1

