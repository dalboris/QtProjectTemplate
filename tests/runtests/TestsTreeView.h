#ifndef TESTSTREEVIEW_H
#define TESTSTREEVIEW_H

#include <QTreeView>

class TestsTreeView: public QTreeView
{
public:
    TestsTreeView(QWidget * parent = nullptr);

    //virtual int sizeHintForColumn(int column) const;
};

#endif // TESTSTREEVIEW_H
