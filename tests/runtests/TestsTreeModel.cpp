// Copyright (C) 2012-2016 The VPaint Developers.
// See the COPYRIGHT file at the top-level directory of this distribution
// and at https://github.com/dalboris/vpaint/blob/master/COPYRIGHT
//
// This file is part of VPaint, a vector graphics editor. It is subject to the
// license terms and conditions in the LICENSE.MIT file found in the top-level
// directory of this distribution and at http://opensource.org/licenses/MIT

#include "TestsTreeModel.h"
#include "TestsTreeItem.h"

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

// Note: caller takes ownership of the QTreeWidgetItems
void populate_(const QDir & dir, const QDir & outDir, TestsTreeItem * parentItem)
{
    // Find test files
    QStringList filters;
    filters << "tst_*.cpp";
    QFileInfoList testFiles = dir.entryInfoList(filters, QDir::Files, QDir::Name);

    // Find subdirs
    QFileInfoList subdirs = dir.entryInfoList(QDir::Dirs | QDir::NoDotAndDotDot, QDir::Name);

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

        // Create item
        QList<QVariant> itemData;
        itemData << name << "" << "PASS";
        TestsTreeItem * item = new TestsTreeItem(itemData, parentItem);
        parentItem->appendChild(item);

        // Recurse
        populate_(subdirDir, subdirOutDir, item);
    }

    // Insert test file items
    for (int i = 0; i < testFiles.size(); ++i)
    {
        //TestRunner * testRunner = new TestRunner(dir, outDir, testFiles[i].fileName());

        // Get test name
        QString name = testFiles[i].baseName();

        // Create item
        QList<QVariant> itemData;
        itemData << name << "" << "PASS";
        TestsTreeItem * item = new TestsTreeItem(itemData, parentItem);
        parentItem->appendChild(item);
    }
}

}

TestsTreeModel::TestsTreeModel(
        const QDir & dir,
        const QDir & outDir,
        QObject * parent) :

    QAbstractItemModel(parent),
    dir_(dir),
    outDir_(outDir)
{
    QList<QVariant> rootData;
    rootData << "Test name" << "" << "Result";
    rootItem = new TestsTreeItem(rootData);
    populate_(dir_, outDir_, rootItem);

    /*
    QList<QVariant> item1Data;
    item1Data <<  "item 1" << "bla bla";
    TestsTreeItem * item1 = new TestsTreeItem(item1Data, rootItem);
    rootItem->appendChild(item1);

    QList<QVariant> item2Data;
    item2Data <<  "item 2" << "blah blah";
    TestsTreeItem * item2 = new TestsTreeItem(item2Data, rootItem);
    rootItem->appendChild(item2);
    */
}

TestsTreeModel::~TestsTreeModel()
{
    delete rootItem;
}

QModelIndex TestsTreeModel::index(int row, int column, const QModelIndex &parent)
            const
{
    if (!hasIndex(row, column, parent))
        return QModelIndex();

    TestsTreeItem *parentItem;

    if (!parent.isValid())
        parentItem = rootItem;
    else
        parentItem = static_cast<TestsTreeItem*>(parent.internalPointer());

    TestsTreeItem *childItem = parentItem->child(row);
    if (childItem)
        return createIndex(row, column, childItem);
    else
        return QModelIndex();
}

QModelIndex TestsTreeModel::parent(const QModelIndex &index) const
{
    if (!index.isValid())
        return QModelIndex();

    TestsTreeItem *childItem = static_cast<TestsTreeItem*>(index.internalPointer());
    TestsTreeItem *parentItem = childItem->parentItem();

    if (parentItem == rootItem)
        return QModelIndex();

    return createIndex(parentItem->row(), 0, parentItem);
}

int TestsTreeModel::rowCount(const QModelIndex &parent) const
{
    TestsTreeItem *parentItem;
    if (parent.column() > 0)
        return 0;

    if (!parent.isValid())
        parentItem = rootItem;
    else
        parentItem = static_cast<TestsTreeItem*>(parent.internalPointer());

    return parentItem->childCount();
}

int TestsTreeModel::columnCount(const QModelIndex &parent) const
{
    if (parent.isValid())
        return static_cast<TestsTreeItem*>(parent.internalPointer())->columnCount();
    else
        return rootItem->columnCount();
}

QVariant TestsTreeModel::data(const QModelIndex &index, int role) const
{
    if (!index.isValid())
        return QVariant();

    if (role == Qt::SizeHintRole)
    {
        if (index.column() == 0)
            return QSize(10,0);
        else if (index.column() == 1)
            return QSize(10,0);
    }

    if (role == Qt::TextAlignmentRole)
    {
        if (index.column() == 0)
            return Qt::AlignLeft;
        else
            return Qt::AlignCenter;
    }

    if (role != Qt::DisplayRole)
        return QVariant();

    TestsTreeItem *item = static_cast<TestsTreeItem*>(index.internalPointer());

    return item->data(index.column());
}

Qt::ItemFlags TestsTreeModel::flags(const QModelIndex &index) const
{
    if (!index.isValid())
        return 0;

    return QAbstractItemModel::flags(index);
}

QVariant TestsTreeModel::headerData(int section, Qt::Orientation orientation,
                               int role) const
{
    if (orientation == Qt::Horizontal && role == Qt::DisplayRole)
        return rootItem->data(section);

    return QVariant();
}
