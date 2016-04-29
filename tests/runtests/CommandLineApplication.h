#ifndef COMMANDLINEAPPLICATION_H
#define COMMANDLINEAPPLICATION_H

#include <QCoreApplication>

class CommandLineApplication: public QCoreApplication
{
    Q_OBJECT

public:
    CommandLineApplication(int argc, char * argv[]);

private slots:
    void runTests_();
};

#endif // COMMANDLINEAPPLICATION_H
