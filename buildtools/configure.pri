# Add python scripts to project
DISTFILES += \
    $$PWD/buildutils.py \
    $$PWD/configure.py \
    $$PWD/makelibtests.py \
    $$PWD/makesubdirstests.py

# Execute configure.py python script
unix:  system(python     configure.py $$_PRO_FILE_PWD_ $$OUT_PWD $$CONFIG)
win32: system(python.exe configure.py $$_PRO_FILE_PWD_ $$OUT_PWD $$CONFIG)
