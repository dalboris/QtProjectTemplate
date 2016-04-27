#include "TestItem.h"

#include "TestRunner.h"

TestItem::TestItem(QObject * parent) :
    QObject(parent),

    parentItem_(nullptr),
    childItems_(),
    row_(0),

    status_(Status::None),
    progress_(0.0)
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

TestItem::Status TestItem::status() const
{
    return status_;
}

double TestItem::progress() const
{
    return progress_;
}

void TestItem::setStatus(TestItem::Status status)
{
    status_ = status;
    emit statusChanged(this);
}

void TestItem::setProgress(double progress)
{
    progress_ = progress;
    emit progressChanged(this);
}
