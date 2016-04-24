#include "DirUtils.h"

#include <QMessageBox>

bool DirUtils::cd(QDir & dir, QString name)
{
    DirUtils::mkdir(dir, name);

    if (dir.cd(name))
    {
        return true;
    }
    else
    {
        QMessageBox::critical(
                0, "Error moving to directory",
                QString("Failed to move to directory %1")
                    .arg(dir.absoluteFilePath(name)));
        return false;
    }
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
