#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This script requires Python >= 2.6. I has been tested with Python 2.7.6 on
# Ubuntu and Windows. It has not yet been tested with Python 3, or on MacOS,
# but might just work.

# NOTE: If you edit this file, then you must manually call
#       qmake for changes to take effect

# Documentation
# -------------
#
# For each project file in the distribution:
#
#     src/Path/To/Project/Project.pro
#
# This script automatically generates an additional project file:
#
#     <build-directory>/Path/To/Project/.config.pri
#
# Which is included by Project.pro.
#
# The automatically generated .config.pri files contain all the boilerplate
# that should normally be manually written in Project.pro, but that can be
# automated, such as:
#
#     1. Specify common configuration options (e.g., C++11 compiler flag)
#
#     2. Set INCLUDEPATH, DEPENDPATH, PRE_TARGETDEPS, and LIBS variables for
#        all platforms, based on the DEPENDS variable of the current project.
#
#     3. Set the SUBDIRS dependencies based on the DEPENDS variable of
#        subprojects
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

# QMake Config
qmakeConfig = sys.argv[3:]


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

# Returns the TEMPLATE value parsed from the given string.
def getTemplate(string):
    match = re.search(r"TEMPLATE\s*=\s*\b(\w+)\b", string)
    if match:
        return match.groups()[0]

# Returns as a list the values of the given qmake variable 'variableName',
# defined in the given inputConfig. Returns an empty list if the variable
# is not found.
#
# Example input:
#
# """
# VARIABLE_I_DONT_CARE = \
#     whatever1 \
#     whatever2 \
#     whatever3
#
# VARIABLE_NAME = \
#     value1 \
#     value2 \
#     value3
# """
#
# Example output:
#
# [ 'value1', 'value2', 'value3' ]
#
# It supports ugly formatting, if you're that kind of person:
#
# VARIABLE_NAME=value1   value2 \
#     value3 \
#   value4 value5
#
# It also supports '/' within values, to specify folders, such as:
#
# SUBDIRS = \
#     Core/Memory \
#     Core/Log \
#     Gui \
#     App
#
# However, it does not support the '+=' syntax.
#
def getVariableValuesAsList(variableName, inputConfig):
    regexPattern = variableName + r"\s*=([^\n\\]*(\\[^\S\n]*\n[^\n\\]*)*)"
    match = re.search(regexPattern, inputConfig)
    if match:
        # Matched string (something like " \\\n    value1 \\\n    value2")
        depends = match.groups()[0]

        # Convert to beautiful list (something like ["value1", "value2"])
        return re.findall(r"[/\w']+", depends)
    else:
        # Return an empty list if not found
        return []

# Returns the DEPENDS value parsed from the given string.
def getDepends(inputConfig):
    return getVariableValuesAsList('DEPENDS', inputConfig)

# Returns the SUBDIRS value parsed from the given string.
def getSubdirs(inputConfig):
    return getVariableValuesAsList('SUBDIRS', inputConfig)

# Returns the project corresponding to the given libname.
# libname is the path of the library relative to Third or Libs.
# Examples:
#     Core
#     Gui/Widgets
#     Gui/Windows
#     Geometry
def getLibProject(libname):
    if ("Third/" + libname) in projects:
        libProject = projects[("Third/" + libname)]
    elif ("Libs/" + libname) in projects:
        libProject = projects[("Libs/" + libname)]
    else:
        libProject = None
        print ("Error: dependent library", libRelDir, "not found. Note: you can only " +
               "depends on 'TEMPLATE = lib' subprojects, maybe you tried to depend on " +
               "a 'TEMPLATE = app' subproject?")
    return libProject


#----------------------- some fixed config texts ------------------------------

headerText = """
# THIS FILE WAS AUTOMATICALLY GENERATED.
# IT IS LOCATED IN THE BUILD DIRECTORY.
# ANY EDIT WILL BE LOST.
"""

generateTestsText = """
# Generate missing unit test files
win32: PYTHON=python.exe
else:  PYTHON=python
system($$PYTHON %1/GenerateTests.py %1 $$_PRO_FILE_PWD_ $$OUT_PWD $$CONFIG)
"""
generateTestsText = generateTestsText.replace('%1', srcDir)

enableCpp11Text = """
# Enable C++11
CONFIG += c++11
"""

prlText = """
# Tell qmake to create a .prl file for this library, and to use it when linking
# against this library. This allows any application that links against this
# library to also link against all libraries that this library depends on.
# I think this is useless since configure.py already computes recursively
# the dependencies and pass them all to the linker in the proper order, but
# to be honest, I don't understand 100% what these .prl files do and it doesn't
# hurt to keep them.
CONFIG += create_prl link_prl
"""

staticLibText = """
# Compile as a static library
CONFIG += staticlib
"""

includeText = """
# Add src/Libs/ and src/Third/ to INCLUDEPATH.
# This fixes "cannot find MyLib/MyHeader.h" compile errors.
INCLUDEPATH += %1/Libs/
INCLUDEPATH += %1/Third/
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM %1/Libs/
unix: QMAKE_CXXFLAGS += $$QMAKE_CFLAGS_ISYSTEM %1/Third/

# Add src/Libs/ and src/Third/ to DEPENDPATH.
# This causes to re-compile dependent .cpp files in this project, whenever
# dependee .h files in src/ are modified. In Qt5, this is redundant with adding
# src/ to INCLUDEPATH, but we keep it for documentation and compatibility with
# Qt4.
DEPENDPATH += %1/Libs/
DEPENDPATH += %1/Third/
"""
includeText = includeText.replace('%1', srcDir)

releaseOrDebugText = """
# Convenient variable whose value is "release" when building
# in release mode, and "debug" when building in debug mode
CONFIG(release, debug|release): RELEASE_OR_DEBUG = release
CONFIG(debug,   debug|release): RELEASE_OR_DEBUG = debug
"""


#------------- text to add a lib this project depends on ----------------------

# Usage:
#     %1: must be replaced by the dependent lib project's name
#     %2: must be replaced by the dependent lib project's srcDir
#     %3: must be replaced by the dependent lib project's outDir

addLibText = """
# Add %1 to LIBS.
# This fixes "undefined reference to `%1::MyFunction()'" linking errors.
unix:  LIBS += -L%3/ -l%1
win32: LIBS += -L%3/$$RELEASE_OR_DEBUG/ -l%1

# Add %1 to PRE_TARGETDEPS.
# This causes to re-link against %1 whenever %1 is recompiled (for instance,
# due a modification of a .cpp file in %1).
unix:       PRE_TARGETDEPS += %3/lib%1.a
win32-g++:  PRE_TARGETDEPS += %3/$$RELEASE_OR_DEBUG/lib%1.a
else:win32: PRE_TARGETDEPS += %3/$$RELEASE_OR_DEBUG/%1.lib
"""


#---------- Project class to store info parsed from the .pro files ------------

# Project class
class Project:

    def __init__(self):

        # Project-related directories and filenames

        self.name = ""      # Project
        self.filename = ""  # Project.pro

        self.relDir = ""    # Path/To/Project
        self.relPath = ""   # Path/To/Project/Project.pro

        self.srcDir = ""    # /home/user/QtProjectTemplate/src/Path/To/Project
        self.srcPath = ""   # /home/user/QtProjectTemplate/src/Path/To/Project/Project.pro

        self.outDir = ""    # /home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/To/Project
        self.outPath = ""   # /home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/To/Project/.config.pri

        # Data parsed from project files

        self.template = ""  # subdirs | lib | app
        self.depends  = []  # Examples:
                            #     []                 for src/Core/Core.pro            (lib)
                            #     [ "Core" ]         for src/Gui/Widgets/Widgets.pro  (lib)
                            #     [ "Gui/Widgets" ]  for src/Gui/Windows/Windows.pro  (lib)
                            #     [ "Gui/Windows" ]  for src/App/App.pro              (app)
                            #     []                 for src/Gui/Gui.pro              (subdirs)
                            #     []                 for src/QtProjectTemplate.pro    (subdirs)
        self.subdirs  = []  # Examples:
                            #     []                        for src/Core/Core.pro            (lib)
                            #     []                        for src/Gui/Widgets/Widgets.pro  (lib)
                            #     []                        for src/Gui/Windows/Windows.pro  (lib)
                            #     []                        for src/App/App.pro              (app)
                            #     [ "Widgets", "Windows"]   for src/Gui/Gui.pro              (subdirs)
                            #     [ "Core", "Gui", "App" ]  for src/QtProjectTemplate.pro    (subdirs)

        # Transitive closure of the .depends relationship

        self.tDependsIsComputed      = False  # Prevent computing more than once
        self.tDependsIsBeingComputed = False  # Detect cyclic dependencies
        self.tDepends = set()                 # Examples:
                                              #     {}                                        for src/Core/Core.pro            (lib)
                                              #     { "Core" }                                for src/Gui/Widgets/Widgets.pro  (lib)
                                              #     { "Gui/Widgets", "Core" }                 for src/Gui/Windows/Windows.pro  (lib)
                                              #     { "Gui/Windows" ,"Core", "Gui/Widgets" }  for src/App/App.pro              (app)
                                              #     {]                                        for src/Gui/Gui.pro              (subdirs)
                                              #     {]                                        for src/QtProjectTemplate.pro    (subdirs)

        # Same as tDepends, but ordered via topological sort
        # This specifies the order in which libs should be linked against.

        self.sDepends = []  # Examples:
                            #     []                                        for src/Core/Core.pro            (lib)
                            #     [ "Core" ]                                for src/Gui/Widgets/Widgets.pro  (lib)
                            #     [ "Core", "Gui/Widgets" ]                 for src/Gui/Windows/Windows.pro  (lib)
                            #     [ "Core", "Gui/Widgets", "Gui/Windows" ]  for src/App/App.pro              (app)
                            #     []                                        for src/Gui/Gui.pro              (subdirs)
                            #     []                                        for src/QtProjectTemplate.pro    (subdirs)

        # Parent/child relationship between projects

        self.parentProject = None
        self.subProjects = []

        # Subdir info dependencies
        # This specifies the order in which subprojects should be built.

        self.subdir    = ""             # To/Project ( = dir of this project relative to parent project)
        self.subdirKey = ""             # To_Project ( = key to identify this subdir without using slashes)
        self.subdirDependsKeys = set()  # Examples:
                                        #     {}                 for src/Core/Core.pro            (lib)
                                        #     {}                 for src/Gui/Widgets/Widgets.pro  (lib)
                                        #     { "Widgets" }      for src/Gui/Windows/Windows.pro  (lib)
                                        #     { "Core", "Gui" }  for src/App/App.pro              (app)
                                        #     { "Core" }         for src/Gui/Gui.pro              (subdirs)
                                        #     {}                 for src/QtProjectTemplate.pro    (subdirs)

# Dictionary storing all projects in the distribution, accessed by their relDir
#
# Example:
#     {
#         ""            : <Project instance> ,
#         "Core"        : <Project instance> ,
#         "Gui/Widgets" : <Project instance> ,
#         "Gui/Windows" : <Project instance> ,
#         "App"         : <Project instance>
#     }
#
projects = {}


#----------------------------- Actual script ----------------------------------

# Write QMake CONFIG value in a file. This is used by tests, so they can link
# against libraries build with the same config. If no folder is found containing
# the same config, then it will create it.

# Find all project files
for x in os.walk(srcDir):
    dirname = x[0].replace('\\', '/') # manually replace backslashes with slashes for Windows
    filenames = x[2]
    relativeDirname = dirname[len(srcDir)+1:]
    for filename in filenames:
        if filename.endswith('.pro'):
            # Create project object
            project = Project()
            project.filename = filename   # "Project.pro"
            project.name = filename[:-4]  # "Project"

            # Get path of directory relative to the root of the distribution
            # This path is used as key to identified the project.
            project.relDir = dirname[len(srcDir)+1:]  # "Path/To/Project"

            # Get relPath, srcDir, and outDir (special case of root project)
            if project.relDir == "":
                project.relPath = project.filename  # "QtProjectTemplate.pro"
                project.srcDir  = srcDir            # "/home/user/QtProjectTemplate/src"
                project.outDir  = outDir            # "/home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug"

            # Get relPath, srcDir, and outDir (normal case of non-root project)
            else:
                project.relPath = project.relDir + '/' + project.filename  # "Path/to/Project/Project.pro"
                project.srcDir = srcDir + '/' + project.relDir             # "/home/user/QtProjectTemplate/src/Path/to/Project"
                project.outDir = outDir + '/' + project.relDir             # "/home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/To/Project"

            # Get srcPath and outPath
            project.srcPath = project.srcDir + '/' + project.filename  # "/home/user/QtProjectTemplate/src/Path/to/Project/Project.pro"
            project.outPath = project.outDir + '/.config.pri'          # "/home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/To/Project/.config.pri"

            # Insert in dictionary storing all projects, using relDir as the key
            projects[project.relDir] = project


# Parse projects
for relDir in projects:
    # Get project
    project = projects[relDir]

    # Get project file as string
    data = read(project.srcPath)

    # Parse TEMPLATE value
    project.template = getTemplate(data)

    # Parse DEPENDS value
    project.depends = getDepends(data)

    # Parse SUBDIRS value
    project.subdirs = getSubdirs(data)


# Helper method:
#
# Computes the transitive closure of project.depends
# and store it in project.tDepends.
#
# What makes this recursive function terminate is
# that for libs which do not depend on any other
# libs, then len(project.depends) == 0 and therefore
# there is no recursion.
#
# Cyclic dependencies are detected and reported as an error.
#
def computeTDepends(project):
    # Do nothing if already computed
    if project.tDependsIsComputed:
        pass

    # Detect cyclic dependencies
    if project.tDependsIsBeingComputed:
        print "Error:", project.name, "has a cyclic dependency."
        pass

    # Mark as being computed
    project.tDependsIsBeingComputed = True

    # Compute
    project.tDepends = set(project.depends)
    for libname in project.depends:
        libProject = getLibProject(libname)
        computeTDepends(libProject)
        project.tDepends = project.tDepends.union(libProject.tDepends)

    # Mark as computedSet isComputed
    project.tDependsIsBeingComputed = False
    project.tDependsIsComputed = True


# Compute the transitive closure of all projects .depends
for relDir in projects:
    # Get project
    project = projects[relDir]

    # Compute tDepends
    computeTDepends(project)


# Compare method for topological sort
def dependsOn(libname1, libname2):
    libProject1 = getLibProject(libname1)
    libProject2 = getLibProject(libname2)
    if libname1 in libProject2.tDepends:
        return -1
    elif libname2 in libProject1.tDepends:
        return +1
    else:
        return 0

# Compute a topological sort to have all transitive dependencies listed in
# order (If lib1 depends on lib2, then lib1 appears after lib1 in the list)
for relDir in projects:
    # Get project
    project = projects[relDir]

    # Compute topological sort
    tDepends = list(project.tDepends)
    project.sDepends = sorted(tDepends, cmp=dependsOn)


# Set parent/child relationships
for relDir in projects:
    # Get project
    project = projects[relDir]

    # For all subdir in subdirs
    for subdir in project.subdirs:
        # Get relDir of subproject
        if project.relDir == "":
            subProjectRelDir = subdir                         # "App"
        else:
            subProjectRelDir = project.relDir + '/' + subdir  # "Gui" + '/' + "src/Gui"

        # Check if subProject exists
        if subProjectRelDir in projects:
            # Get subproject
            subProject = projects[subProjectRelDir]

            # Set parent/child relationships
            project.subProjects.append(subProject)
            subProject.parentProject = project
            subProject.subdir = subdir
            subProject.subdirKey = subdir.replace('/', '__')

        else:
            print ("Error: subproject", subProjectRelDir, "of project", project.relDir, "not found.")


# Helper method:
#
# Returns a list of all ancestors of a project. The first element of the
# returned list is the root project of the distribution, and the last element
# is the given project.
#
def getAncestors(project):
    ancestors = [project]
    while ancestors[0].parentProject != None:
        ancestors.insert(0, ancestors[0].parentProject)
    return ancestors


# Resolve subdirs dependencies based on lib/app dependencies
for relDir in projects:
    # Get project
    project = projects[relDir]

    # For all lib/app dependency
    for libname in project.sDepends:
        # Get project of the lib this project depends on
        libProject = getLibProject(libname)

        # Get all ancestors of this project and of libProject
        projectAncestors = getAncestors(project)
        libProjectAncestors = getAncestors(libProject)

        # Find common ancestor
        indexCommonAncestor = 0
        while projectAncestors[indexCommonAncestor+1] == libProjectAncestors[indexCommonAncestor+1]:
            indexCommonAncestor += 1

        # Add subdir dependency
        dependentProject = projectAncestors[indexCommonAncestor+1]
        dependeeProject  = libProjectAncestors[indexCommonAncestor+1]
        dependentProject.subdirDependsKeys.add(dependeeProject.subdirKey)


# Generate all .config.pri files
for relDir in projects:
    # Get project
    project = projects[relDir]

    # Create directory containing this project's .config.pri
    mkdir_p(project.outDir)

    # Create .config.pri file and open it
    f = open(project.outPath, 'w')

    # Write header
    f.write(headerText)

    # Write python call to generate unit tests
    if project.template == "lib" and project.relDir.startswith('Libs/'):
        f.write(generateTestsText)

    # Enable C++11
    if project.template == "lib" or project.template == "app":
        f.write(enableCpp11Text)

    # Insert PRL config lines
    if project.template == "lib" or project.template == "app":
        f.write(prlText)

    # Adds all headers of the distribution in include path
    if project.template == "lib" or project.template == "app":
        f.write(includeText)

    # Compile as a static library
    if project.template == "lib":
        f.write(staticLibText)

    # If project is a subdir
    if project.template == "subdirs":
        # Override value of SUBDIRS by using keys instead of folder path
        subdirsText = ("\n" +
                       "# Override value of SUBDIRS by using keys instead of folder path\n" +
                       "SUBDIRS =")
        for subProject in project.subProjects:
            subdirsText += " \\\n    " + subProject.subdirKey
        subdirsText += "\n"
        f.write(subdirsText)

        # Set subdirs and dependencies
        for subProject in project.subProjects:
            subdirText = ("\n" +
                          "# Set " + subProject.subdirKey + " location and dependencies\n")
            subdirText += subProject.subdirKey + ".subdir  = " + subProject.subdir + "\n"
            subdirText += subProject.subdirKey + ".depends ="
            for key in subProject.subdirDependsKeys:
                subdirText += " " + key
            subdirText += "\n"
            f.write(subdirText)

    # Add text required whenever there is at least one lib dependency
    if len(project.sDepends) > 0:
        f.write(releaseOrDebugText)

    # Add each dependent lib in order
    # Note that we use the reversed topological order since
    # each library must appear in the linker command line *before* the
    # libraries they depend on. This is counter-intuitive, but that's how it is.
    #
    for libname in reversed(project.sDepends):
        libProject = getLibProject(libname)
        addThisLib = (addLibText.replace('%1', libProject.name)
                                .replace('%2', libProject.srcDir)
                                .replace('%3', libProject.outDir))
        f.write(addThisLib)

    # Close file
    f.close()
