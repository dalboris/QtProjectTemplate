#ifndef TESTSTREEVIEW_H
#define TESTSTREEVIEW_H

#include <QTreeView>
#include <QModelIndex>

class TestTreeView: public QTreeView
{
    Q_OBJECT

public:
    TestTreeView(QWidget * parent = nullptr);

    virtual void setModel(QAbstractItemModel * model);

    //virtual int sizeHintForColumn(int column) const;

private:
    QModelIndex firstChild_(const QModelIndex & parentIndex);
    QModelIndex nextSibling_(const QModelIndex & index);
    void makeRunButtonsOfChildren_(const QModelIndex & parentIndex = QModelIndex());
};

#endif // TESTSTREEVIEW_H
