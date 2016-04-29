#include "CommandLineApplication.h"
#include <QTimer>

CommandLineApplication::CommandLineApplication(int argc, char * argv[]) :
    QCoreApplication(argc, argv)
{
    qDebug("Command line app.");

    QTimer::singleShot(0, this, SLOT(runTests_()));
}

void CommandLineApplication::runTests_()
{
    qDebug("Running tests...");
    qDebug("Done.");
    quit();
}
