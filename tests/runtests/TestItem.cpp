#include "TestItem.h"

#include "TestRunner.h"

TestItem::TestItem(QObject * parent) :
    QObject(parent),
    parentItem_(nullptr),
    childItems_(),
    row_(0)
{
}

TestItem::~TestItem()
{
}

TestItem * TestItem::parentItem() const
{
    return parentItem_;
}

TestItem * TestItem::childItem(int row) const
{
    return childItems_.value(row);
}

int TestItem::numChildItems() const
{
    return childItems_.count();
}

int TestItem::row() const
{
    return row_;
}

void TestItem::appendChildItem(TestItem * childItem)
{
    childItem->row_ = numChildItems();
    childItems_.append(childItem);
    childItem->setParent(this);
    childItem->parentItem_ = this;
}
