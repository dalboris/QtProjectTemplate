#include "DirUtils.h"

#include <QMessageBox>

bool DirUtils::cd(QDir & dir, QString relPath)
{
    QStringList names = relPath.split('/');
    foreach (QString name, names)
    {
        DirUtils::mkdir(dir, name);

        if (!dir.cd(name))
        {
            QMessageBox::critical(
                        0, "Error moving to directory",
                        QString("Failed to move to directory %1")
                        .arg(dir.absoluteFilePath(name)));
            return false;
        }
    }
    return true;
}

bool DirUtils::mkdir(QDir & dir, QString name)
{
    if (dir.exists(name))
    {
        return true;
    }
    else
    {
        if (dir.mkdir(name))
        {
            return true;
        }
        else
        {
            QMessageBox::critical(
                    0, "Error creating directory",
                    QString("Failed to create directory %1")
                        .arg(dir.absoluteFilePath(name)));
            return false;
        }
    }
}

QDir DirUtils::rootDir()
{
    // Note: num of cdUp() depends on win32/unix
    QDir res = QDir(QMAKE_PWD);
    while (res.dirName() != "tests")
        res.cdUp();
    res.cdUp();
    return res;
}

QDir DirUtils::rootOutDir()
{
    // Note: num of cdUp() depends on win32/unix
    QDir res = QDir(QMAKE_OUT_PWD);
    while (res.dirName() != "tests")
        res.cdUp();
    res.cdUp();
    return res;
}

QDir DirUtils::dir(const QString & relPath)
{
    QDir res = rootDir();
    cd(res, relPath);
    return res;
}

QDir DirUtils::outDir(const QString & relPath)
{
    QDir res = rootOutDir();
    cd(res, relPath);
    return res;
}
