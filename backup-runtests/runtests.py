import subprocess

print "runtests.py"

sp = subprocess.Popen("./Test_Gui_Windows_MainWindow", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = sp.communicate()
if out:
    print "standard output of subprocess:"
    print out
if err:
    print "standard error of subprocess:"
    print err
print "returncode of subprocess:"
print sp.returncode
