
#-----------------------------------------------------------------------------#
#          IMPORTANT: If you edit this file, then you must manually           #
#                     call qmake for changes to take effect                   #
#-----------------------------------------------------------------------------#

# Documentation
# -------------
#
# For each project file in the distribution:
#
#     src/Path/To/Project/Project.pro
#
# This script automatically generates an additional project file:
#
#     <build-directory>/Path/To/Project/AutoBuild.pri
#
# Which is included by Project.pro.
#
# The automatically generated AutoBuild.pri file contains all the boilerplate
# that should normally be manually written in Project.pro, but that can be
# automated, such as:
#
#     1. Specify C++11 compiler flags.
#
#     2. Sets INCLUDEPATH and LIBS variables for all platforms, based on
#        the DEPENDS variable
#
#     3. Set the SUBDIRS dependencies based on the DEPENDS variable of
#        subprojects
#
# This avoids code duplication and increases readability/maintainability.
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

# Creates a directory and all its parent (if they don't already exist)
def mkdir_p(dirpath):
    try:
        os.makedirs(dirpath)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(dirpath):
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


#----------------------- some fixed config texts ------------------------------

headerText = """
# THIS FILE WAS AUTOMATICALLY GENERATED.
# IT IS LOCATED IN THE BUILD DIRECTORY.
# ANY EDIT WILL BE LOST.
"""

enableCpp11Text = """
# Enable C++11
CONFIG += c++11
"""

staticLibText = """
# Compile as a static library
CONFIG += staticlib
"""

addSelfToIncludePathText = """
# Add this lib project to its own INCLUDEPATH
INCLUDEPATH += $$_PRO_FILE_PWD_/../
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM $$_PRO_FILE_PWD_/../
"""


#------------- text to add a lib this project depends on ----------------------

releaseOrDebugText = """
# Convenient variable whose value is "release" when building
# in release mode, and "debug" when building in debug mode
CONFIG(release, debug|release): RELEASE_OR_DEBUG = release
CONFIG(debug,   debug|release): RELEASE_OR_DEBUG = debug
"""

# %1: must be replaced by the dependent lib project's name
# %2: must be replaced by the dependent lib project's srcDir
# %3: must be replaced by the dependent lib project's outDir

addLibText = """
# Add %1 to INCLUDEPATH.
# This fixes "cannot find %1/Foo.h" compile errors.
INCLUDEPATH += %2/../
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM %2/../

# Add %1 to LIBS.
# This fixes "undefined reference to `Foo::Foo()'" linking errors.
unix:  LIBS += -L%3/ -l%1
win32: LIBS += -L%3/RELEASE_OR_DEBUG # XXX double-check on Windows

# Add %1 to DEPENDPATH.
# This adds all headers in %1 to the list of headers that qmake parses to
# generate dependencies. In other words, this causes to recompile relevant
# files from this project whenever dependent headers from %1 change.
# This is in fact useless now: since Qt5, folders added to INCLUDEPATH
# are now automatically considered by qmake to generate dependencies. However,
# we keep it here since it doesn't hurt, and might help if someone wants
# to use the AutoBuild.py script with Qt4.
DEPENDPATH += %2/../

# Add %1 to PRE_TARGETDEPS.
# This causes to re-link this project whenever %1 is recompiled. This is
# important, otherwise modifying a .cpp file in %1 would not cause this
# project to link to the new version of %1, and therefore the change
# would not be seen.
unix:       PRE_TARGETDEPS += %3/lib%1.a
win32-g++:  PRE_TARGETDEPS += %3/RELEASE_OR_DEBUG/lib%1.a
else:win32: PRE_TARGETDEPS += %3/RELEASE_OR_DEBUG/%1.lib
"""


#---------- Project class to store info parsed from the .pro files ------------

# Project class
class Project:

    def __init__(self):
        self.name = ""      # Project
        self.filename = ""  # Project.pro

        self.srcDir = ""    # /home/user/QtProjectTemplate/src/Path/To/Project
        self.srcPath = ""   # /home/user/QtProjectTemplate/src/Path/To/Project/Project.pro

        self.outDir = ""    # /home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/To/Project
        self.outPath = ""   # /home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/To/Project/AutoBuild.pri

        self.template = ""  # subdir | lib | app
        self.depends  = []  # [ "Lib1", "Lib2" ]

# List storing all projects in the distribution
projects = []

# Dictionary to get a lib project from its name
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
            project.outPath = project.outDir + '/AutoBuild.pri'

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


# Generate all AutoBuild.pri files
for project in projects:

    # Create directory containing this project's AutoBuild.pri
    mkdir_p(project.outDir)

    # Create AutoBuild.pri file and open it
    f = open(project.outPath, 'w')

    # Write header
    f.write(headerText)

    # Enable C++11
    if project.template == "lib" or project.template == "app":
        f.write(enableCpp11Text)

    # If project is a lib
    if project.template == "lib":
        # Compile as a static library
        f.write(staticLibText)

        # Add self to INCLUDEPATH
        f.write(addSelfToIncludePathText)

    # Add text required whenever there is at least one lib dependency
    if len(project.depends) > 0:
        f.write(releaseOrDebugText)

    # Add each dependent lib
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
