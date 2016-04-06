
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

# Returns the TEMPLATE value parsed from the given string.
def getTemplate(string):
    match = re.search(r"TEMPLATE\s*=\s*\b(\w+)\b", string)
    if match:
        return match.groups()[0]

# Returns the DEPENDS value parsed from the given string.
def getDepends(string):
    match = re.search(r"DEPENDS\s*=([^\n\\]*(\\[^\S\n]*\n[^\n\\]*)*)", string)
    if match:
        # raw parsed value, e.g.: " \\\n    Lib1 \\\n    Lib2"
        depends = match.groups()[0]

        # clean list, e.g. ["Lib1", "Lib2"]
        return re.findall(r"[/\w']+", depends)
    else:
        return []

# Returns the SUBDIRS value parsed from the given string.
def getSubdirs(string):
    match = re.search(r"SUBDIRS\s*=([^\n\\]*(\\[^\S\n]*\n[^\n\\]*)*)", string)
    if match:
        # raw parsed value, e.g.: " \\\n    src/Gui \\\n    tests/GuiTests"
        subdirs = match.groups()[0]

        # clean list, e.g. ["src/Gui", "tests/GuiTests"]
        return re.findall(r"[/\w']+", subdirs)
    else:
        return []

# Returns the project corresponding to the given libname.
def getLibProject(libname):
    if libname in libs:
        return libs[libname]
    else:
        print ("Error: dependent library", libname, "not found. Note: you can only " +
               "depends on 'TEMPLATE = lib' subprojects, maybe you tried to depend on " +
               "a 'TEMPLATE = app' subproject?")


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

prlText = """
# Tell qmake to create a .prl file for this library, and to use it when linking
# against this library. This allows any application that links against this
# library to also link against all libraries that this library depends on.
# This is normally not necessary since AutoBuild.py also compute recursively
# the dependencies and pass them all to the linker in the proper order, but
# it doesn't hurt to keep these as well.
CONFIG += create_prl
CONFIG += link_prl
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
# This fixes "undefined reference to `%1::Foo::Foo()'" linking errors.
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

        # Project-related directories and filenames

        self.name = ""      # Project
        self.filename = ""  # Project.pro

        self.relDir = ""    # Path/To/Project
        self.relPath = ""   # Path/To/Project/Project.pro

        self.srcDir = ""    # /home/user/QtProjectTemplate/src/Path/To/Project
        self.srcPath = ""   # /home/user/QtProjectTemplate/src/Path/To/Project/Project.pro

        self.outDir = ""    # /home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/To/Project
        self.outPath = ""   # /home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/To/Project/AutoBuild.pri


        # Data parsed from project files

        self.template = ""  # subdir | lib | app
        self.depends  = []  # [ "Gui" ]
        self.subdirs  = []  # [ "Core", "Gui", "App" ], [ "src/Gui", "tests/GuiTests" ], etc.


        # Transitive closure of the .depends relationship

        self.tDepends           = set()  # { "Gui", "Core" } if self.depends = [ "Gui" ] and Gui.depends = [ "Core" ]
        self.tDependsIsComputed      = False  # Prevent computing more than once
        self.tDependsIsBeingComputed = False  # Detect cyclic dependencies


        # Same set as above, but ordered via topological sort

        self.sDepends = []  # [ "Core", "Gui" ] if self.tDepends = { "Gui", "Core" } and Gui.depends = [ "Core" ]


        # Parent/child relationship between projects

        self.parentProject = None
        self.subProjects = []


        # Subdir info and resolved dependencies

        self.subdir    = ""             # To/Project ( = dir of this project relative to parent project)
        self.subdirKey = ""             # To_Project ( = key to identify this subdir)
        self.subdirDependsKeys = set()  # Keys of subdirs that this subdir depends on. Examples:
                                        #    subdirKey              subdirDependsKeys
                                        #     "Core"           ->    {}
                                        #     "Gui"            ->    {"Core"}
                                        #     "App"            ->    {"Core", "Gui"}
                                        #     "src_Gui"        ->    {}
                                        #     "tests_GuiTests" ->    {"src_Gui"}
                                        #
                                        # These keys are always keys of sibling subdirs


# Dictionary storing all projects in the distribution, accessed by their relDir
# Example of keys:
#     - "" (root project)
#     - "Gui"
#     - "Gui/src/Gui"
#     - "Gui/tests/GuiTests"
#     - "App"
projects = {}

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
            project.filename = filename   # "Project.pro"
            project.name = filename[:-4]  # "Project"

            # Get path of directory relative to the root of the distribution
            # This path is used as key to identified the project.
            project.relDir = dirname[len(srcDir)+1:]  # "Path/to/Project"

            # Get relPath, srcDir, and outDir (special case of root project)
            if project.relDir == "":
                project.relPath = project.filename  # "RootProject.pro"
                project.srcDir  = srcDir            # "/home/user/QtProjectTemplate/src"
                project.outDir  = outDir            # "/home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug"

            # Get relPath, srcDir, and outDir (normal case of non-root project)
            else:
                project.relPath = project.relDir + '/' + project.filename  # "Path/to/Project/Project.pro"
                project.srcDir = srcDir + '/' + project.relDir             # "/home/user/QtProjectTemplate/src/Path/to/Project"
                project.outDir = outDir + '/' + project.relDir             # "/home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/to/Project"

            # Get srcPath and outPath
            project.srcPath = project.srcDir + '/' + project.filename  # "/home/user/QtProjectTemplate/src/Path/to/Project/Project.pro"
            project.outPath = project.outDir + '/AutoBuild.pri'        # "/home/user/QtProjectTemplate/build-Qt_5_5_GCC_64bit-Debug/Path/to/Project/AutoBuild.pro"

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

    # If project is a lib, add it to libs
    if project.template == "lib":
        libs[project.name] = project


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
    print "sDepends(", relDir, ") =", project.sDepends


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


# Generate all AutoBuild.pri files
for relDir in projects:
    # Get project
    project = projects[relDir]

    # Create directory containing this project's AutoBuild.pri
    mkdir_p(project.outDir)

    # Create AutoBuild.pri file and open it
    f = open(project.outPath, 'w')

    # Write header
    f.write(headerText)

    # Enable C++11
    if project.template == "lib" or project.template == "app":
        f.write(enableCpp11Text)

    # Insert PRL config lines
    if project.template == "lib" or project.template == "app":
        f.write(prlText)

    # Compile as a static library
    if project.template == "lib":
        f.write(staticLibText)

    # Add self to INCLUDEPATH
    if project.template == "lib":
        f.write(addSelfToIncludePathText)

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
