#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------- Required modules ---------------------------------

# Built-in modules
import sys
import os
import shutil
import errno
import re

# Curstom module
import buildutils


#--------------- Arguments passed to this script by qmake ---------------------

# <root-dir> directory
rootDir = sys.argv[1]

# <root-out-dir> directory (= build directory)
rootOutDir = sys.argv[2]

# lib's src directory     ( e.g., <root-dir>/src/libs/a/b/Lib )
srcLibDir = sys.argv[3]

# lib's src out directory ( e.g., <root-out-dir>/src/libs/a/b/Lib )
srcLibOutDir = sys.argv[4]

# qmake CONFIG variable value
config = sys.argv[5:]


#--------------- Useful configuration variables -------------------------------

# Test if building on a Unix system
# This is determined by the presence of "unix" in CONFIG
if 'unix' in config:
    unix = True
else:
    unix = False

# Test if building on a Windows system
# This is determined by the presence of "win32" in CONFIG
if 'win32' in config:
    win32 = True
else:
    win32 = False

# Test if building in release or debug mode
# This is determined by which of 'release' and 'debug' appears last in CONFIG
release = True
debug = False
for s in config:
    if s == 'release':
        release = True
        debug = False
    elif s == 'debug':
        release = False
        debug = True

# Convenient variable holding a string equals to either 'release' or 'debug'
if release:
    releaseOrDebug = 'release'
else:
    releaseOrDebug = 'debug'

# Python command depending on OS
if win32:
    pythonCmd = 'python.exe'
else:
    pythonCmd = 'python'


#---------------------- Various useful variables ------------------------------

# root directories
srcDir       = rootDir + '/src'         # <root-dir>/src
srcLibsDir   = rootDir + '/src/libs'    # <root-dir>/src/libs
testsDir     = rootDir + '/tests'       # <root-dir>/tests
testsLibsDir = rootDir + '/tests/libs'  # <root-dir>/tests/libs

# root out directories
srcOutDir       = rootOutDir + '/src'         # <root-out-dir>/src
srcLibsOutDir   = rootOutDir + '/src/libs'    # <root-out-dir>/src/libs
testsOutDir     = rootOutDir + '/tests'       # <root-out-dir>/tests
testsLibsOutDir = rootOutDir + '/tests/libs'  # <root-out-dir>/tests/libs

# lib's name and directory relative to src/libs/
libName   = os.path.basename(srcLibDir)      # Lib
libRelDir = srcLibDir[len(srcLibsDir)+1:]    # a/b/Lib
libRelDirPreSlashed = ""                     # /a/b/Lib
if libRelDir != "":
    libRelDirPreSlashed = '/' + libRelDir

# lib's tests directory
testsLibDir = testsLibsDir + libRelDirPreSlashed        # <root-dir>/tests/libs/a/b/Lib

# lib's tests out directory
testsLibOutDir = testsLibsOutDir + libRelDirPreSlashed  # <root-out-dir>/tests/libs/a/b/Lib

# Prefixes
testPrefix    = 'Test_'                           # Test_
libPrefix     = libRelDir.replace('/','_') + '_'  # a_b_Lib_
testLibPrefix = testPrefix + libPrefix            # Test_a_b_Lib_


#---------------------- Get test dependencies ------------------------------

# Read lib's src .config.pri file
srcLibPriFilePath    = srcLibOutDir + '/.config.pri'
srcLibPriFileContent = buildutils.readFromFile(srcLibPriFilePath)

# Parse dependencies
qt_sdepends    = buildutils.getQmakeVariable('QT_SDEPENDS',    srcLibPriFileContent)
third_sdepends = buildutils.getQmakeVariable('THIRD_SDEPENDS', srcLibPriFileContent)
lib_sdepends   = buildutils.getQmakeVariable('LIB_SDEPENDS',   srcLibPriFileContent)

# Add this lib to dependencies
lib_sdepends.append(libRelDir)


#---------------- Class to store info about a header's test -------------------

class HeaderTest:

    def __init__(self):

        self.headerPath = ""  # <root-dir>/src/libs/a/b/Lib/c/d/Foo.h

        self.headerFileName = ""     # Foo.h
        self.headerRelDir = ""       # c/d
        self.headerRelPath = ""      # c/d/Foo.h
        self.headerIncludePath = ""  # /a/b/Lib/c/d/Foo.h

        self.headerName = ""  # Foo
        self.testName = ""    # Test_a_b_Lib_Foo

        self.testRelDir = ""  # c/d/Test_a_b_Lib_Foo

        self.testProFileName = ""  # Test_a_b_Lib_Foo.pro
        self.testHFileName = ""    # Test_a_b_Lib_Foo.h
        self.testCppFileName = ""  # Test_a_b_Lib_Foo.cpp

        self.testDir = ""          # <root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo
        self.testProFilePath = ""  # <root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.pro
        self.testHFilePath = ""    # <root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.h
        self.testCppFilePath = ""  # <root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.cpp

        self.testOutDir = ""       # <root-out-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo
        self.testPriFilePath = ""  # <root-out-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/.config.pri

# All HeaderTests, access by their testRelDir
headerTests = {}


#------------ Find all headers for which a test should be created -------------

# Find all header files
for x in os.walk(srcLibDir):
    dir = x[0].replace('\\', '/')        # <root-dir>/src/libs/a/b/Lib/c/d
    relDir = dir[len(srcLibDir)+1:]      # c/d
    filenames = x[2]                     # [ 'Foo.h', 'Foo.cpp', 'Bar.h', 'Bar.cpp' ]
    for filename in filenames:
        if filename.endswith('.h'):
            # Create HeaderTest object
            headerTest = HeaderTest()

            # Set attribute values
            headerTest.headerPath = dir + '/' + filename  # /home/<user>/<root-dir>/src/libs/a/b/Lib/c/d/Foo.h

            headerTest.headerFileName = filename   # Foo.h
            headerTest.headerRelDir   = relDir     # c/d

            headerTest.headerName = filename[:-2]                          # Foo
            headerTest.testName   = testLibPrefix + headerTest.headerName  # Test_a_b_Lib_Foo

            relDirSlashed = ("" if relDir == "" else relDir + '/')       # c/d/                  (or "", but never just "/")
            headerTest.testRelDir = relDirSlashed + headerTest.testName  # c/d/Test_a_b_Lib_Foo  (note: we don't use join because if relDir == "",
                                                                         #                              it would produce "./Test_a_b_Lib_Foo" while
                                                                         #                              we want "Test_a_b_Lib_Foo")

            headerTest.headerRelPath     = relDirSlashed + headerTest.headerFileName     # c/d/Foo.h
            headerTest.headerIncludePath = libRelDir + '/' + headerTest.headerRelPath # a/b/Lib/c/d/Foo.h

            headerTest.testProFileName = headerTest.testName + '.pro'  # Test_a_b_Lib_Foo.pro
            headerTest.testHFileName   = headerTest.testName + '.h'    # Test_a_b_Lib_Foo.h
            headerTest.testCppFileName = headerTest.testName + '.cpp'  # Test_a_b_Lib_Foo.cpp

            headerTest.testDir         = testsLibDir + '/' + headerTest.testRelDir               # /home/<user>/<root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo
            headerTest.testProFilePath = headerTest.testDir + '/' + headerTest.testProFileName   # /home/<user>/<root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.pro
            headerTest.testHFilePath   = headerTest.testDir + '/' + headerTest.testHFileName     # /home/<user>/<root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.h
            headerTest.testCppFilePath = headerTest.testDir + '/' + headerTest.testCppFileName   # /home/<user>/<root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.cpp

            headerTest.testOutDir      = testsLibOutDir + '/' + headerTest.testRelDir            # /home/<user>/<build-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo
            headerTest.testPriFilePath = headerTest.testOutDir + "/.config.pri"                  # /home/<user>/<build-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/.config.pri

            # Add to dictionary of all HeaderTests
            headerTests[headerTest.testRelDir] = headerTest


#-------------------- Make lib's test folder and project ----------------------

# Get file for this test project
libProFileName = libName + '.pro'
testsLibProFilePath = os.path.join(testsLibDir, libProFileName)

# Generate content for <root-dir>/tests/libs/a/b/Lib/Lib.pro
testsLibProFileContent  = (
"""
#####################################################################
#   This file was automatically generated. Any edit will be lost.   #
#####################################################################

TEMPLATE = subdirs
SUBDIRS = \\
    $$OUT_PWD/.runtests"""
)

for testRelDir in sorted(headerTests):
    testsLibProFileContent += " \\\n    " + testRelDir
testsLibProFileContent += "\n"

# Write content to <root-dir>/tests/libs/a/b/Lib/Lib.pro
testsLibProFilePath = os.path.join(testsLibDir, libProFileName)
buildutils.writeToFileIfDifferent(testsLibProFilePath, testsLibProFileContent)

# Create $$OUT_PWD/.runtests project with all the files it contains
runtestsDir = os.path.join(testsLibOutDir, '.runtests')
buildutils.writeToFile(os.path.join(runtestsDir, '.runtests.pro'), buildutils.runtests_pro)
buildutils.writeToFile(os.path.join(runtestsDir, 'runtests.cpp'), buildutils.runtests_cpp)
buildutils.writeToFile(os.path.join(runtestsDir, 'runtests.py'), buildutils.runtests_py)


#------------- text to add a lib this project depends on ----------------------

addLibTextUnix = (
"""
# Add dependency to %libRelDir
LIBS += -L%libOutDir/ -l%libname
PRE_TARGETDEPS += %libOutDir/lib%libname.a
"""
)

addLibTextWin32 = (
"""
# Add dependency to %libRelDir
LIBS += -L%libOutDir/%releaseOrDebug/ -l%libname
PRE_TARGETDEPS += %libOutDir/%releaseOrDebug/%libname.lib
"""
.replace('%releaseOrDebug', releaseOrDebug)
)

if unix:
    addLibText = addLibTextUnix
else:
    addLibText = addLibTextWin32


#------------- Make header's test .config.pri, .pro, .h, and .cpp file -------------

testProFileText = (
"""
#####################################################################
#   This file was automatically generated. Any edit will be lost.   #
#####################################################################

TEMPLATE = app
HEADERS = %testname.h
SOURCES = %testname.cpp

include($$OUT_PWD/.config.pri)
"""
)

testPriFileCommonText = (
"""
#####################################################################
#   This file was automatically generated. Any edit will be lost.   #
#####################################################################

CONFIG += c++11

INCLUDEPATH += %rootDir/tests/testsuite/
INCLUDEPATH += %rootDir/src/libs/
INCLUDEPATH += %rootDir/src/third/
"""
.replace('%rootDir', rootDir)
)

testPriFileCommonTextUnixOnly = (
"""
QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM %rootDir/src/third/
"""
.replace('%rootDir', rootDir)
)

if unix:
    testPriFileCommonText += testPriFileCommonTextUnixOnly

# Full content of pri file. Note: for now, all header tests for given library
# have the same pri file. But this may change in the future, so let's keep them
# duplicated.
testPriFileContent = testPriFileCommonText

# Add each dependent library in order from most dependent to least dependent.

# Internal libraries
for libname in reversed(lib_sdepends):
    relDir = 'libs/' + libname
    outDir = srcOutDir + '/libs/' + libname
    basename = os.path.basename(outDir)
    addThisLib = (addLibText.replace('%libRelDir', relDir)
                            .replace('%libOutDir', outDir)
                            .replace('%libname',   basename))
    testPriFileContent += addThisLib

# Third-party libraries
for libname in reversed(third_sdepends):
    relDir = 'third/' + libname
    outDir = srcOutDir + '/third/' + libname
    basename = os.path.basename(outDir)
    addThisLib = (addLibText.replace('%libRelDir', relDir)
                            .replace('%libOutDir', outDir)
                            .replace('%libname',   basename))
    testPriFileContent += addThisLib

# Qt libraries
testPriFileContent += (
"""
# Add dependency to Qt
QT = %qt testlib
"""
.replace('%qt', " ".join(qt_sdepends))
)


testCppFileText = (
"""
/*********************************************************************
 *   This file was automatically generated. Any edit will be lost.   *
 *********************************************************************/

#include "%testname.h"
TEST_DEFINE_MAIN(%testname)
"""
)

testHFileText = (
"""
#include <CoreTest.h>
#include <%headerIncludePath>

class %testname: public QObject
{
    Q_OBJECT

private slots:

    void test() // <- rename test function
    {
        // ... test things here ...
    }

    // ... create other test functions here ...
};
"""
)

for testRelDir in headerTests:
    # Get HeaderTest
    headerTest = headerTests[testRelDir]

    # Make project file for this header test
    content = testProFileText.replace('%testname', headerTest.testName)
    buildutils.writeToFileIfDifferent(headerTest.testProFilePath, content)

    # Make .config.pri file for this header test
    buildutils.writeToFileIfDifferent(headerTest.testPriFilePath, testPriFileContent)

    # Make C++ file for this header test
    testCppFileContent = testCppFileText.replace('%testname', headerTest.testName)
    buildutils.writeToFileIfDifferent(headerTest.testCppFilePath, testCppFileContent)

    # Make header file for this header test
    if not os.path.isfile(headerTest.testHFilePath):
        testHFileContent = testHFileText.replace('%headerIncludePath', headerTest.headerIncludePath).replace('%testname', headerTest.testName)
        buildutils.writeToFile(headerTest.testHFilePath, testHFileContent)
