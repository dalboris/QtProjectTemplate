// Copyright (C) 2012-2016 The VPaint Developers.
// See the COPYRIGHT file at the top-level directory of this distribution
// and at https://github.com/dalboris/vpaint/blob/master/COPYRIGHT
//
// This file is part of VPaint, a vector graphics editor. It is subject to the
// license terms and conditions in the LICENSE.MIT file found in the top-level
// directory of this distribution and at http://opensource.org/licenses/MIT

#ifndef TESTSTREEMODEL_H
#define TESTSTREEMODEL_H

#include <QAbstractItemModel>
#include <QDir>

class TestsTreeItem;

class TestsTreeModel : public QAbstractItemModel
{
    Q_OBJECT

public:
    explicit TestsTreeModel(
            const QDir & dir,
            const QDir & outDir,
            QObject * parent = nullptr);

    ~TestsTreeModel();

    QVariant data(const QModelIndex & index, int role) const Q_DECL_OVERRIDE;
    Qt::ItemFlags flags(const QModelIndex & index) const Q_DECL_OVERRIDE;
    QVariant headerData(int section, Qt::Orientation orientation,
                        int role = Qt::DisplayRole) const Q_DECL_OVERRIDE;
    QModelIndex index(int row, int column,
                      const QModelIndex & parent = QModelIndex()) const Q_DECL_OVERRIDE;
    QModelIndex parent(const QModelIndex & index) const Q_DECL_OVERRIDE;
    int rowCount(const QModelIndex & parent = QModelIndex()) const Q_DECL_OVERRIDE;
    int columnCount(const QModelIndex & parent = QModelIndex()) const Q_DECL_OVERRIDE;

private:
    TestsTreeItem * rootItem;

    QDir dir_;
    QDir outDir_;
};
#endif // TESTSTREEMODEL_H
