#ifndef TESTSTREEITEM_H
#define TESTSTREEITEM_H

#include <QList>
#include <QVariant>

class TestsTreeItem
{
public:
    explicit TestsTreeItem(const QList<QVariant> & data,
                           TestsTreeItem *parentItem = nullptr);
    ~TestsTreeItem();

    void appendChild(TestsTreeItem * child);

    TestsTreeItem * child(int row);
    int childCount() const;
    int columnCount() const;
    QVariant data(int column) const;
    int row() const;
    TestsTreeItem * parentItem();

private:
    QList<TestsTreeItem*> childItems_;
    QList<QVariant> itemData_;
    TestsTreeItem * parentItem_;
};
#endif // TESTSTREEITEM_H
