#ifndef DIRTESTITEM_H
#define DIRTESTITEM_H

#include "TestItem.h"
#include <QDir>

class DirTestItem: public TestItem
{
public:
    DirTestItem(const QDir & dir,
                const QDir & outDir,
                QObject * parent = nullptr);

    virtual QString name() const;
    virtual QString status() const;

    virtual QString output() const;
    virtual QString compileOutput() const;
    virtual QString runOutput() const;

    virtual void run();

private:
    QDir dir_;
};

#endif // DIRTESTITEM_H
