#include "TestsTreeWidget.h"

#include <QMessageBox>

namespace
{

bool mkdir_(QDir & dir, QString name)
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

bool cd_(QDir & dir, QString name)
{
    mkdir_(dir, name);

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

QTreeWidgetItem * makeItem_(const QString & name)
{
    return new QTreeWidgetItem((QTreeWidget*) nullptr, QStringList(name));
}

// Note: caller takes ownership of the QTreeWidgetItems
QList<QTreeWidgetItem *> getChildren_(const QDir & dir, const QDir & outDir)
{
    // Find test files
    QStringList filters;
    filters << "tst_*.cpp";
    QFileInfoList testFiles = dir.entryInfoList(filters, QDir::Files, QDir::Name);

    // Find subdirs
    QFileInfoList subdirs = dir.entryInfoList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name);

    // Output
    QList<QTreeWidgetItem *> items;

    // Insert subdir items
    for (int i = 0; i < subdirs.size(); ++i)
    {
        // Get subdir name
        QString name = subdirs[i].fileName();

        // Cd to subdir dirs (call mkdir if necessary)
        QDir subdirDir = dir;
        QDir subdirOutDir = outDir;
        if (!cd_(subdirDir, name) || !cd_(subdirOutDir, name))
            continue;

        // Recurse
        QList<QTreeWidgetItem *> children = getChildren_(subdirDir, subdirOutDir);
        QTreeWidgetItem * item = makeItem_(name);
        item->insertChildren(0, children);

        // Insert item
        items.append(item);
    }

    // Insert test file items
    for (int i = 0; i < testFiles.size(); ++i)
    {
        QString name = testFiles[i].baseName();
        QTreeWidgetItem * item = makeItem_(name);
        items.append(item);
    }

    // Return items
    return items;
}

}

TestsTreeWidget::TestsTreeWidget(const QDir & dir, const QDir & outDir, QWidget * parent) :
    QTreeWidget(parent),
    dir_(dir),
    outDir_(outDir)
{
    setSizePolicy(QSizePolicy::Preferred, QSizePolicy::Expanding);
    setColumnCount(1);
    setHeaderHidden(true);
    insertTopLevelItems(0, getChildren_(dir_, outDir_));
}
