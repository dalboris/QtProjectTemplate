#include "DirTestItem.h"
#include "FileTestItem.h"
#include "DirUtils.h"

DirTestItem::DirTestItem(
        const QDir & dir,
        const QDir & outDir,
        QObject * parent) :

    TestItem(parent),
    dir_(dir)
{
    // Find subdirs
    QFileInfoList subdirs = dir.entryInfoList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name);

    // Append subdir child items
    for (int i = 0; i < subdirs.size(); ++i)
    {
        // Get subdir name
        QString name = subdirs[i].fileName();

        // Cd to subdir dirs (this implicitely calls mkdir if necessary)
        QDir subdirDir = dir;
        QDir subdirOutDir = outDir;
        if (!DirUtils::cd(subdirDir, name) || !DirUtils::cd(subdirOutDir, name))
            continue;

        // Create child item
        DirTestItem * item = new DirTestItem(subdirDir, subdirOutDir);
        appendChildItem(item);
    }

    // Find test files
    QStringList filters;
    filters << "tst_*.cpp";
    QFileInfoList testFiles = dir.entryInfoList(filters, QDir::Files, QDir::Name);

    // Append test file child items
    for (int i = 0; i < testFiles.size(); ++i)
    {
        // Get fileName
        QString fileName = testFiles[i].fileName();

        // Create child item
        FileTestItem * item = new FileTestItem(dir, outDir, fileName);
        appendChildItem(item);
    }
}

QString DirTestItem::name() const
{
    return dir_.dirName();
}

QString DirTestItem::status() const
{
    return "";
}

QString DirTestItem::output() const
{
    return "";
}

QString DirTestItem::compileOutput() const
{
    return "";
}

QString DirTestItem::runOutput() const
{
    return "";
}

void DirTestItem::run()
{
    for (int i=0; i<numChildItems(); ++i)
    {
        childItem(i)->run();
    }
}
