
# Preliminary build step
DISTFILES += build.py
win32: PYTHON=python.exe
else:  PYTHON=python
system($$PYTHON build.py $$PWD $$OUT_PWD)

# Subdirs
TEMPLATE = subdirs
SUBDIRS += \
    App1 \
    App2
