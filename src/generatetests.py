#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------- Required modules ---------------------------------

import buildutils

buildutils.printsomething()

import sys
import os
import errno


#---------------------- Various useful variables ------------------------------

# root directories
srcDir       = sys.argv[1]            # /home/<user>/<root-dir>/src
srcLibsDir   = srcDir + '/libs'       # /home/<user>/<root-dir>/src/libs
testsDir     = srcDir[:-3] + 'tests'  # /home/<user>/<root-dir>/tests
testsLibsDir = testsDir + '/libs'     # /home/<user>/<root-dir>/tests/libs

# lib's source directory
srcLibDir    = sys.argv[2]                      # /home/<user>/<root-dir>/src/libs/a/b/Lib
srcLibRelDir = srcLibDir[len(srcLibsDir)+1:]    # a/b/Lib
libName      = os.path.basename(srcLibRelDir)   # Lib

# lib's tests directory
testsLibDir = testsLibsDir + '/' + srcLibRelDir # /home/<user>/<root-dir>/tests/libs/a/b/Lib

# lib's build target directory
libOutDir = sys.argv[3]                         # /home/<user>/<build-dir>/src/libs/a/b/Lib

# QMake Config
qmakeConfig = sys.argv[4:]

# Prefixes
testPrefix    = 'Test_'                               # Test_
libPrefix     = srcLibRelDir.replace('/','_') + '_'   # a_b_Lib_
testLibPrefix = testPrefix + libPrefix                # Test_a_b_Lib_


#---------------- Class to store info about a header's test -------------------

class HeaderTest:

    def __init__(self):

        self.headerPath = ""  # /home/<user>/<root-dir>/src/libs/a/b/Lib/c/d/Foo.h

        self.headerFileName = ""  # Foo.h
        self.headerRelDir = ""    # c/d

        self.headerName = ""  # Foo
        self.testName = ""    # Test_a_b_Lib_Foo

        self.testRelDir = ""  # c/d/Test_a_b_Lib_Foo

        self.testProFileName = ""  # Test_a_b_Lib_Foo.pro
        self.testCppFileName = ""  # Test_a_b_Lib_Foo.cpp

        self.testDir = ""          # /home/<user>/<root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo
        self.testProFilePath = ""  # /home/<user>/<root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.pro
        self.testCppFilePath = ""  # /home/<user>/<root-dir>/tests/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.cpp

# All HeaderTests, access by their testRelDir
headerTests = {}


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


#------------ Find all headers for which a test should be created -------------

# Find all header files
for x in os.walk(srcLibDir):
    dir = x[0].replace('\\', '/')        # /home/<user>/<root-dir>/src/libs/a/b/Lib/c/d
    relDir = dir[len(srcLibDir)+1:]  # c/d
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

            headerTest.testProFileName = headerTest.testName + '.pro'  # Test_a_b_Lib_Foo.pro
            headerTest.testCppFileName = headerTest.testName + '.cpp'  # Test_a_b_Lib_Foo.cpp

            headerTest.testDir         = testsLibDir + '/' + headerTest.testRelDir               # /home/<user>/<root-dir>/test/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo
            headerTest.testProFilePath = headerTest.testDir + '/' + headerTest.testProFileName   # /home/<user>/<root-dir>/test/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.pro
            headerTest.testCppFilePath = headerTest.testDir + '/' + headerTest.testCppFileName   # /home/<user>/<root-dir>/test/libs/a/b/Lib/c/d/Test_a_b_Lib_Foo/Test_a_b_Lib_Foo.cpp

            # Add to dictionary of all HeaderTests
            headerTests[headerTest.testRelDir] = headerTest


#-------------------- Make lib's test folder and project ----------------------

# Make directory for this lib test
mkdir_p(testsLibDir)

# Get file for this test project
testsLibProFileName = libName + '.pro'
testsLibProFilePath = os.path.join(testsLibDir, testsLibProFileName)

# Generate new text for this project file.
testsLibProText  = "# This file is automatically generated. Any edit will be lost.\n"
testsLibProText += "# It is kept in source control for readability on GitHub.\n\n"
testsLibProText += "TEMPLATE = subdirs\n"
testsLibProText += "SUBDIRS ="
for testRelDir in sorted(headerTests):
    testsLibProText += " \\\n    " + testRelDir
testsLibProText += "\n"

# Get existing text if the project file already exists.
if os.path.isfile(testsLibProFilePath):
    f = open(testsLibProFilePath, 'r')
    testsLibProOldText = f.read()
    f.close()
else:
    testsLibProOldText = ""

# If the new text and the existing text differ, then write new text to file
if testsLibProText != testsLibProOldText:
    f = open(testsLibProFilePath, 'w')
    f.write(testsLibProText)
    f.close()


#------------- Make header's test folder, project, and cpp file -------------

for testRelDir in headerTests:
    # Get HeaderTest
    headerTest = headerTests[testRelDir]

    # Make directory for this header test
    mkdir_p(headerTest.testDir)

    # Make project file for this header test
    f = open(headerTest.testProFilePath, 'w')
    f.write("TEMPLATE = app\nSOURCES = " + headerTest.testCppFileName + "\n")
    f.close()

    # Make C++ file for this header test
    f = open(headerTest.testCppFilePath, 'w')
    f.write("#include <iostream>\nint main() { std::cout << \"Hello World\\n\"; }\n")
    f.close()
