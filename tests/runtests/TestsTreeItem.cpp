// Copyright (C) 2012-2016 The VPaint Developers.
// See the COPYRIGHT file at the top-level directory of this distribution
// and at https://github.com/dalboris/vpaint/blob/master/COPYRIGHT
//
// This file is part of VPaint, a vector graphics editor. It is subject to the
// license terms and conditions in the LICENSE.MIT file found in the top-level
// directory of this distribution and at http://opensource.org/licenses/MIT

#include "TestsTreeItem.h"

TestsTreeItem::TestsTreeItem(
        const QList<QVariant> & data,
        TestsTreeItem * parent) :

    itemData_(data),
    parentItem_(parent)
{
}

TestsTreeItem::~TestsTreeItem()
{
    qDeleteAll(childItems_);
}

void TestsTreeItem::appendChild(TestsTreeItem * item)
{
    childItems_.append(item);
}

TestsTreeItem * TestsTreeItem::child(int row)
{
    return childItems_.value(row);
}

int TestsTreeItem::childCount() const
{
    return childItems_.count();
}

int TestsTreeItem::row() const
{
    if (parentItem_)
        return parentItem_->childItems_.indexOf(const_cast<TestsTreeItem*>(this));

    return 0;
}

int TestsTreeItem::columnCount() const
{
    return itemData_.count();
}

QVariant TestsTreeItem::data(int column) const
{
    return itemData_.value(column);
}

TestsTreeItem * TestsTreeItem::parentItem()
{
    return parentItem_;
}
