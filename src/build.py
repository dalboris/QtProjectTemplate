# Note: If you edit this file, then you must manually call qmake for changes to
# take effect

import sys
import os
import shutil

srcDir = sys.argv[1]
outDir = sys.argv[2]

# For each *.pro file in srcDir
for x in os.walk(srcDir):
    dirname = x[0]
    filenames = x[2]
    relativeDirname = dirname[len(srcDir)+1:]
    for filename in filenames:
	if filename.endswith('.pro'):
	    # 1. Print that we are processing the *.pro file
	    print "  Processing", filename

	    # 2. Get relevant directories associated with this *.pro file
	    relativeDirname = dirname[len(srcDir)+1:]
	    if relativeDirname == "":
		proSrcDir = srcDir
		proOutDir = outDir
	    else:
		proSrcDir = srcDir + '/' + relativeDirname
		proOutDir = outDir + '/' + relativeDirname

	    # 3. Create Build.pri file
	    f = open(proOutDir + '/Build.pri', 'w')
	    f.write("# THIS FILE WAS AUTOMATICALLY GENERATED.\n" +
		    "# IT IS LOCATED IN THE BUILD DIRECTORY.\n" +
		    "# ANY EDIT WILL BE LOST.\n\n")
	    f.write("message(Hello from " + filename + ")\n")
	    f.close()
