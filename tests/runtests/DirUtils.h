#ifndef DIRUTILS_H
#define DIRUTILS_H

#include <QDir>
#include <QString>

class DirUtils
{
public:
    static bool cd(QDir & dir, QString name);
    static bool mkdir(QDir & dir, QString name);
};

#endif // DIRUTILS_H
