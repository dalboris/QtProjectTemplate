#ifndef FILETESTITEM_H
#define FILETESTITEM_H

#include "TestItem.h"
#include "TestRunner.h"

class QDir;

class FileTestItem: public TestItem
{
    Q_OBJECT

public:
    FileTestItem(const QDir & dir,
                 const QDir & outDir,
                 const QString & fileName,
                 QObject * parent = nullptr);

    virtual QString name() const;
    virtual QString status() const;
    virtual void run();

private slots:
    void onStatusChanged_(TestRunner::Status status);

private:
    TestRunner * testRunner_;
};

#endif // FILETESTITEM_H
