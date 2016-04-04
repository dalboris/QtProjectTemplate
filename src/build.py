#
# build.py
#
# Note: If you edit this file, then you must manually
#       call qmake for changes to take effect
#

#--------------------------- Required modules ---------------------------------

import sys
import os
import shutil
import errno
import re


#--------------- Arguments passed to this script by qmake ---------------------

# Source directory (where qmake builds from)
srcDir = sys.argv[1]

# Output build directory (where qmake builds to)
outDir = sys.argv[2]


#--------------------------- Helper functions ---------------------------------

# Creates the directory "path" and all its parent if they don't already exist
def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# Reads file
def read(filepath):
    f = open(filepath, 'r')
    filedata = f.read()
    f.close()
    return filedata

# Gets TEMPLATE value
def getTemplate(string):
    match = re.search(r"TEMPLATE\s*=\s*\b(\w+)\b", string)
    if match:
        return match.groups()[0]

# Gets DEPENDS value
def getDepends(string):
    match = re.search(r"DEPENDS\s*=([^\n\\]*(\\[^\S\n]*\n[^\n\\]*)*)", string)
    if match:
        # raw parsed value, e.g.: " \\\n    Lib1 \\\n    Lib2"
        depends = match.groups()[0]

        # clean list, e.g. ["Lib1", "Lib2"]
        return re.findall(r"[\w']+", depends)
    else:
        return []


#--------------- config text common to all .pro files -------------------------

commonText = """
# THIS FILE WAS AUTOMATICALLY GENERATED.
# IT IS LOCATED IN THE BUILD DIRECTORY.
# ANY EDIT WILL BE LOST.

# Enable C++11
CONFIG += c++11

# Convenient variable whose value is "release" when building
# in release mode, and "debug" when building in debug mode
CONFIG(release, debug|release): RELEASE_OR_DEBUG = release
CONFIG(debug,   debug|release): RELEASE_OR_DEBUG = debug
"""


#---------------- text to add itself to include path --------------------------

addItselfToIncludePathText = """
# Add itself to INCLUDEPATH
INCLUDEPATH += $$_PRO_FILE_PWD_/../
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$_PRO_FILE_PWD_/../
"""


#---------- text to add a lib to INCLUDEPATH and to LIBS ----------------------

# %1: must be replaced by the project's name
# %2: must be replaced by the project's srcDir
# %3: must be replaced by the project's outDir

addLibText = """
# Add %1 to INCLUDEPATH (i.e., fix "cannot find %1/Foo.h" compile errors)
INCLUDEPATH += %2/../
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM %2/../

# Add %1 to LIBS (i.e., fix "undefined reference to `Foo::Foo()'" linking errors)
unix:  LIBS += -L%3/ -l%1
win32: LIBS += -L%3/RELEASE_OR_DEBUG # XXX double-check on Windows
"""


#---------- Project class to store info parsed from the .pro files ------------

class Project:

    def __init__(self):
        self.name = ""      # Lib1
        self.filename = ""  # Lib1.pro

        self.srcDir = ""    # /home/user/QtProjectTemplate/src/Lib1
        self.srcPath = ""   # /home/user/QtProjectTemplate/src/Lib1/Lib1.pro

        self.outDir = ""    # /home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Lib1
        self.outPath = ""   # /home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Lib1/_.pri

        self.template = ""  # subdir | lib | app
        self.depends  = []  # [ "Lib1", "Lib2" ]

projects = []
libs = {}


#----------------------------- Actual script ----------------------------------

# Find all project files
for x in os.walk(srcDir):
    dirname = x[0]
    filenames = x[2]
    relativeDirname = dirname[len(srcDir)+1:]
    for filename in filenames:
        if filename.endswith('.pro'):

            # Create project object
            project = Project()
            project.filename = filename
            project.name = filename[:-4]

            # Get relevant directories associated with this project
            relativeDirname = dirname[len(srcDir)+1:]
            if relativeDirname == "":
                project.srcDir = srcDir
                project.outDir = outDir
            else:
                project.srcDir = srcDir + '/' + relativeDirname
                project.outDir = outDir + '/' + relativeDirname
            project.srcPath = project.srcDir + '/' + project.filename
            project.outPath = project.outDir + '/_.pri'

            # Insert in list of projects
            projects.append(project)

# Parse projects
for project in projects:

    # Get project file as string
    data = read(project.srcPath)

    # Parse TEMPLATE value
    project.template = getTemplate(data)

    # Parse DEPENDS value
    project.depends = getDepends(data)

    # If project is a lib, add it to libs
    if project.template == "lib":
        libs[project.name] = project


# Create all _pri files
for project in projects:

    # Create directory where it's gonna live
    mkdir_p(project.outDir)

    # Create file and open it
    f = open(project.outPath, 'w')

    # Write common stuff
    f.write(commonText)

    # If project is a lib, add itself to INCLUDEPATH
    f.write(addItselfToIncludePathText)

    # If project is a lib, ensure it is created as a static library
    f.write("\n# Create as a static library\nCONFIG += staticlib\n")

    # Add dependent libs to INCLUDEPATH and to LIBS
    for lib in project.depends:
        if lib in libs:
            libProject = libs[lib]
            addThisLib = (addLibText.replace('%1', libProject.name)
                                    .replace('%2', libProject.srcDir)
                                    .replace('%3', libProject.outDir))
            f.write(addThisLib)
        else:
            print ("Error: dependent library", lib, "not found. Note: you can only " +
                   "depends on 'TEMPLATE = lib' subprojects, maybe you tried to depend on " +
                   "a 'TEMPLATE = app' subproject?")

    # Close file
    f.close()


