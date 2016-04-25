#ifndef TESTITEM_H
#define TESTITEM_H

#include <QObject>
#include <QList>
#include <QString>

class TestRunner;

/// \class TestItem
/// \brief A class to represent an item in the TestTreeModel
///
/// This is a virtual class. It is inherited by FileTestItem (the leaves of
/// the test tree), and DirTestItem (the non-leaf nodes of the test tree).
///
/// The parentItem of each item (= parent node for test tree) is also its
/// parent QObject (= parent for memory management). The root of the test
/// tree have a null parentItem, but it has a non-null parent QObject.
/// Its parent QObject is the TestTreeModel that manages it.
///
/// Apart from the root item, there is no need to specify the parent
/// QObject of TestItems: both the parentItem and the parent QObject
/// are automatically set when calling appendChildItem().
///
/// When creating a DirTestItem, it auto-populates itself of its child
/// items in the constructor.
///
class TestItem: public QObject
{
    Q_OBJECT

public:
    TestItem(QObject * parent = nullptr);
    virtual ~TestItem()=0;

    // Parent-child hierarchy
    TestItem * parentItem() const;
    TestItem * childItem(int row) const;
    int numChildItems() const;
    int row() const;

    // Data
    virtual QString name() const=0;
    virtual QString status() const=0;

    // Output
    virtual QString output() const=0;
    virtual QString compileOutput() const=0;
    virtual QString runOutput() const=0;

public slots:
    // Run test
    virtual void run()=0;

signals:
    void statusChanged(TestItem * item);
    void outputChanged();

protected:
    void appendChildItem(TestItem * childItem);

private:
    TestItem * parentItem_;
    QList<TestItem*> childItems_;
    int row_;
};

#endif // TESTSTREEITEM_H
