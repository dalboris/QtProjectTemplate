#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------- Required modules ---------------------------------

# Built-in modules
import sys
import os
import shutil
import errno
import re

# Custom module
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


#----------------------------- Actual script ----------------------------------


# Get file content of <root-dir>/src/libs/a/b/Lib/Lib.pro
libProFileName = libName + '.pro'
srcLibProFilePath = os.path.join(srcLibDir, libProFileName)
srcLibProFileContent = buildutils.readFromFile(srcLibProFilePath)

# Read subdirs
subdirs = buildutils.getQmakeVariable('SUBDIRS', srcLibProFileContent)

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

for subdir in sorted(subdirs):
    testsLibProFileContent += " \\\n    " + subdir
testsLibProFileContent += "\n"

# Write content to <root-dir>/tests/libs/a/b/Lib/Lib.pro
testsLibProFilePath = os.path.join(testsLibDir, libProFileName)
buildutils.writeToFileIfDifferent(testsLibProFilePath, testsLibProFileContent)

# Create $$OUT_PWD/.runtests project with all the files it contains
runtestsDir = os.path.join(testsLibOutDir, '.runtests')
buildutils.writeToFile(os.path.join(runtestsDir, '.runtests.pro'), buildutils.runtests_pro)
buildutils.writeToFile(os.path.join(runtestsDir, 'runtests.cpp'), buildutils.runtests_cpp)
buildutils.writeToFile(os.path.join(runtestsDir, 'runtests.py'), buildutils.runtests_py)
