#!/usr/bin/env python
# -*- coding: utf-8 -*-

#--------------------------- Required modules ---------------------------------

import sys
import os


#--------------- Arguments passed to this script by qmake ---------------------

# src directory
srcDir = sys.argv[1]

# tests directory
testsDir = srcDir[:-3] + 'tests'

# lib's source code directory
libSrcDir = sys.argv[2]

# lib's source code directory relative to src directory
libRelDir = libSrcDir[len(srcDir)+1:]

# lib's unit tests directory
libTestsDir = testsDir + '/' + libRelDir

# lib's build target directory
libOutDir = sys.argv[3]

# QMake Config
qmakeConfig = sys.argv[4:]


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


#----------------------------- Actual script ----------------------------------

mkdir_p(libTestsDir)
