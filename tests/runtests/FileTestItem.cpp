#include "FileTestItem.h"

FileTestItem::FileTestItem(
        const QDir & dir,
        const QDir & outDir,
        const QString & fileName,
        QObject *parent) :

    TestItem(parent)
{
    testRunner_ = new TestRunner(dir, outDir, fileName, this);
    connect(testRunner_, &TestRunner::statusChanged, this, &FileTestItem::onStatusChanged_);
}

QString FileTestItem::name() const
{
    return testRunner_->testName();
}

QString FileTestItem::status() const
{
    TestRunner::Status status = testRunner_->status();

    switch (status)
    {
    case TestRunner::Status::NotCompiledYet:
        return "";
    case TestRunner::Status::Compiling:
        return "Compiling...";
    case TestRunner::Status::CompileError:
        return "COMPILE ERROR";
    case TestRunner::Status::NotRunYet:
        return "COMPILED";
    case TestRunner::Status::Running:
        return "Running...";
    case TestRunner::Status::RunError:
        return "FAIL";
    case TestRunner::Status::Pass:
        return "PASS";
    }

    return "";
}

void FileTestItem::run()
{
    testRunner_->run();
}

void FileTestItem::onStatusChanged_(TestRunner::Status /*status*/)
{
    emit statusChanged(this);
}
