#include "TestTreeView.h"
#include "TestItem.h"

#include <QPushButton>

TestTreeView::TestTreeView(QWidget *parent) :
    QTreeView(parent)
{

}

void TestTreeView::setModel(QAbstractItemModel * model)
{
    QTreeView::setModel(model);
    makeRunButtonsOfChildren_();
}

QModelIndex TestTreeView::firstChild_(const QModelIndex & parentIndex)
{
    if (model())
        return model()->index(0, 0, parentIndex);
    else
        return QModelIndex();
}

QModelIndex TestTreeView::nextSibling_(const QModelIndex & index)
{
    return index.sibling(index.row()+1, 0);
}

void TestTreeView::makeRunButtonsOfChildren_(const QModelIndex & parentIndex)
{
    if (!model())
        return;

    for(QModelIndex index = firstChild_(parentIndex);
        index.isValid();
        index = nextSibling_(index))
    {
        // Create QPushButton
        QPushButton * button = new QPushButton();
        button->setMinimumSize(16, 16);
        button->setMaximumSize(16, 16);
        button->setIcon(QIcon(":/runicon.png"));
        button->setFlat(true);
        button->setStyleSheet(
                    "QPushButton {border: none}"
                    "QPushButton:hover:!pressed {background-color: rgba(150,150,150, 0.3);}"
                    "QPushButton:hover:pressed  {background-color: rgba(150,150,150, 0.6);}");

        // Connect to run function
        TestItem * item = static_cast<TestItem*>(index.internalPointer());
        connect(button, &QPushButton::clicked, item, &TestItem::run);

        // Insert in View
        QModelIndex buttonIndex = index.sibling(index.row(), 1);
        setIndexWidget(buttonIndex, button);

        // Recurse on children
        makeRunButtonsOfChildren_(index);
    }
}
