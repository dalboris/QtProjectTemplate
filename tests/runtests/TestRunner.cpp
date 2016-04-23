#include "TestRunner.h"

#include <QFile>
#include <QDateTime>
#include <QTextStream>
#include <QStringRef>
#include <QVector>
#include <QProcess>

#include <QtDebug>

namespace
{

QString generateH(const QString & testName, const QString & testSource)
{
    // Find BEGIN_TESTS and END_TESTS
    const QString beginTests = "BEGIN_TESTS";
    const QString endTests   = "END_TESTS";
    const int beginTestsIndex = testSource.indexOf(beginTests);
    const int endTestsIndex   = testSource.indexOf(endTests);

    // Report errors
    if (beginTestsIndex == -1)           return "#error BEGIN_TESTS not found";
    if (endTestsIndex   == -1)           return "#error END_TESTS not found";
    if (endTestsIndex < beginTestsIndex) return "#error END_TESTS appears before BEGIN_TESTS";

    // Get everything before BEGIN_TESTS
    const QString testHeader = testSource.left(beginTestsIndex);

    // Get everything between BEGIN_TESTS and END_TESTS
    const QString testFunctions = testSource.mid(
                beginTestsIndex + beginTests.size(),
                endTestsIndex - beginTestsIndex - beginTests.size());

    // Get everything after END_TESTS
    const QString testFooter = testSource.mid(endTestsIndex + endTests.size());

    // Template string
    QString out =
            "%testHeader"
            "class %testName: public QObject\n"
            "{\n"
            "    Q_OBJECT\n"
            "\n"
            "private slots:"
            "%testFunctions"
            "};"
            "%testFooter";

    // Replace placeholders in template
    out.replace("%testHeader",    testHeader)
       .replace("%testName",      testName)
       .replace("%testFunctions", testFunctions)
       .replace("%testFooter",    testFooter);

    // Replace `#include "Test.h"` by `#include <QTest>`
    out.replace(QRegExp("#include\\s+\"Test.h\""), "#include <QTest>");

    // Return generated tst_Foo.gen.h
    return out;
}

QString generateCpp(const QString & testName)
{
    // Template string
    QString out =
            "#include \"%testName.gen.h\"\n"
            "#include <%appType>\n"
            "\n"
            "int main(int argc, char *argv[])\n"
            "{\n"
            "    %appType app(argc, argv);\n"
            "    QCoreApplication::setAttribute(Qt::AA_Use96Dpi, true);\n"
            "    QTEST_SET_MAIN_SOURCE_PATH\n"
            "    %testName test;\n"
            "    return QTest::qExec(&test, argc, argv);\n"
            "}\n";

    // Replace placeholders in template
    out.replace("%appType",   "QApplication")
       .replace("%testName", testName);

    // Return generated tst_Foo.gen.cpp
    return out;
}

QString generatePro(const QString & testName)
{
    // Template string
    QString out =
            "TEMPLATE = app\n"
            "CONFIG += c++11\n"
            "QT += widgets testlib\n" // XXX TODO: widgets should only be for QApplication
            "\n" // XXX TODO: Add library dependencies here
            "HEADERS += %testName.gen.h\n"
            "SOURCES += %testName.gen.cpp\n";

    // Replace placeholders in template
    out.replace("%testName", testName);

    // Return generated tst_Foo.gen.pro
    return out;
}

QString getCurrentTime()
{
    return QTime::currentTime().toString("HH:mm:ss");
}

}

TestRunner::TestRunner(const QDir & inDir,
                       const QDir & outDir,
                       const QString & fileName,
                       QObject * parent) :
    QObject(parent),

    inDir_(inDir),
    outDir_(outDir),
    fileName_(fileName),

    status_(Status::NotCompiledYet),
    compileOutput_(),
    runOutput_()
{
    process_ = new QProcess(this);
}

TestRunner::Status TestRunner::status() const
{
    return status_;
}


QString TestRunner::compileOutput() const
{
    return compileOutput_;
}

QString TestRunner::runOutput() const
{
    return runOutput_;
}

QString TestRunner::output() const
{
    QString res;

    switch (status())
    {
    case Status::NotCompiledYet:
        res = QString();
        break;

    case Status::Compiling:
    case Status::CompileError:
    case Status::NotRunYet:
        res = compileOutput();
        break;

    case Status::Running:
    case Status::RunError:
    case Status::Pass:
        res = runOutput();
        break;
    }

    return res;
}

void TestRunner::failCompilation_(const QString & errorMessage)
{
    QString time = getCurrentTime();
    compileOutput_ += time + ": Compilation failed: " + errorMessage + "\n";
    status_ = Status::CompileError;
    emit compileFinished(false);
}

void TestRunner::compile()
{
    // Get info about test source
    const QString filePath = inDir_.filePath(fileName_);
    const QFileInfo fileInfo(filePath);
    const QDateTime lastModified = fileInfo.lastModified();
    const QString testName = fileInfo.baseName();
    testName_ = testName;

    // Compile if necessary
    Status s = status();
    bool notCompiledYet = (s == Status::NotCompiledYet) || (s == Status::CompileError);
    bool modified       = (lastCompiled_ < lastModified);
    bool processing     = (s == Status::Compiling) || (s == Status::Running);
    if (notCompiledYet || (modified && !processing))
    {
        status_ = Status::Compiling;
        compileOutput_.clear();
        lastCompiled_ = lastModified;

        // -------- Go to folder where to compile test --------

        QString compileDirPath = outDir_.absoluteFilePath(testName);
        compileDir_ = outDir_;
        if (!compileDir_.cd(testName))
        {
            // Create folder since it doesn't exist
            if (!outDir_.mkdir(testName))
            {
                failCompilation_("Can't create build folder " + compileDirPath);
                return;
            }

            // Go to folder where to compile test
            // This is hard to reach (if we manage to create the folder, surely
            // we can cd to it), but doesn't hurt to check.
            if (!compileDir_.cd(testName))
            {
                failCompilation_("Can't create build folder " + compileDirPath);
                return;
            }
        }


        // -------- Open all files for reading or writing --------

        const QString hFileName   = testName + ".gen.h";
        const QString cppFileName = testName + ".gen.cpp";
        const QString proFileName = testName + ".gen.pro";

        const QString hFilePath   = compileDir_.filePath(hFileName);
        const QString cppFilePath = compileDir_.filePath(cppFileName);
        const QString proFilePath = compileDir_.filePath(proFileName);

        QFile sourceFile(filePath);
        QFile hFile(hFilePath);
        QFile cppFile(cppFilePath);
        QFile proFile(proFilePath);

        if (!sourceFile.open(QFile::ReadOnly | QFile::Text))
        {
            failCompilation_("Can't open " + filePath);
            return;
        }

        if (!hFile.open(QFile::WriteOnly | QFile::Text))
        {
            failCompilation_("Can't write " + hFilePath);
            return;
        }

        if (!cppFile.open(QFile::WriteOnly | QFile::Text))
        {
            failCompilation_("Can't write " + cppFilePath);
            return;
        }

        if (!proFile.open(QFile::WriteOnly | QFile::Text))
        {
            failCompilation_("Can't write " + proFilePath);
            return;
        }


        // -------- Read source file --------

        QTextStream sourceStream(&sourceFile);
        const QString testSource = sourceStream.readAll();


        // -------- Generate and write test gen files --------

        QTextStream hStream(&hFile);
        QTextStream cppStream(&cppFile);
        QTextStream proStream(&proFile);

        hStream   << generateH(testName, testSource);
        cppStream << generateCpp(testName);
        proStream << generatePro(testName);


        // -------- Run qmake --------

        QString program = QMAKE_QMAKE_QMAKE;
        QStringList arguments;
        arguments << "-spec" << QMAKE_QMAKESPEC << proFilePath;

        compileOutput_ +=
                getCurrentTime() +
                ": Starting: \"" +
                program + "\" " +
                arguments.join(' ') + "\n";

        process_->setWorkingDirectory(compileDirPath);
        connect(process_,
                static_cast<void (QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
                this,
                &TestRunner::compile_onQmakeFinished_);
        process_->start(program, arguments);

        // -> go read qMakeFinished_(int exitCode) now.
    }
    else
    {
        emit compileFinished(true);
    }
}

void TestRunner::compile_onQmakeFinished_(int exitCode, QProcess::ExitStatus /*exitStatus*/)
{
    process_->disconnect();

    compileOutput_ += process_->readAll();
    if (exitCode == 0)
    {
        // -------- Output end of qmake --------

        QString time = getCurrentTime();
        compileOutput_ += time + ": The process \"" + process_->program() + "\" exited normally.\n";


        // -------- Run make --------

        QString program = "make"; // XXX TODO check that this works on Windows too
        QStringList arguments;

        compileOutput_ +=
                getCurrentTime() +
                ": Starting: \"" +
                program + "\" " +
                arguments.join(' ') + "\n";

        connect(process_,
                static_cast<void (QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
                this,
                &TestRunner::compile_onMakeFinished_);
        process_->start(program, arguments);

        // -> go read makeFinished_(int exitCode) now.
    }
    else
    {
        QString time = getCurrentTime();
        compileOutput_ +=
                time + ": The process \"" + process_->program() +
                QString("\" exited with code %1.\n").arg(exitCode);
        failCompilation_("qmake failed.");
    }
}


void TestRunner::compile_onMakeFinished_(int exitCode, QProcess::ExitStatus /*exitStatus*/)
{
    process_->disconnect();

    compileOutput_ += process_->readAll();
    if (exitCode == 0)
    {
        QString time = getCurrentTime();
        compileOutput_ += time + ": The process \"" + process_->program() + "\" exited normally.\n";

        testBinPath_ = compileDir_.absoluteFilePath(testName_); // XXX TODO change this on Windows
        status_ = Status::NotRunYet;
        emit compileFinished(true);
    }
    else
    {
        QString time = getCurrentTime();
        compileOutput_ +=
                time + ": The process \"" + process_->program() +
                QString("\" exited with code %1.\n").arg(exitCode);
        failCompilation_("make failed.");
    }
}

void TestRunner::run()
{
    runOutput_.clear();
    connect(this, &TestRunner::compileFinished, this, &TestRunner::run_onCompileFinished_);
    compile();
}

void TestRunner::run_onCompileFinished_(bool success)
{
    disconnect(this, &TestRunner::compileFinished, this, &TestRunner::run_onCompileFinished_);

    if (success)
    {
        status_ = Status::Running;

        // -------- Run test --------

        QString program = testBinPath_;
        QStringList arguments;

        runOutput_ +=
                getCurrentTime() +
                ": Starting: \"" +
                program + "\" " +
                arguments.join(' ') + "\n";

        connect(process_,
                static_cast<void (QProcess::*)(int, QProcess::ExitStatus)>(&QProcess::finished),
                this,
                &TestRunner::run_onTestFinished_);
        process_->start(program, arguments);
    }
    else
    {
        emit runFinished(false);
    }
}



void TestRunner::run_onTestFinished_(int exitCode, QProcess::ExitStatus /*exitStatus*/)
{
    process_->disconnect();

    runOutput_ += process_->readAll();

    if (exitCode == 0)
    {
        QString time = getCurrentTime();
        runOutput_ += time + ": The process \"" + process_->program() + "\" exited normally.\n";
        runOutput_ += time + ": Test passed :-)\n";

        status_ = Status::Pass;
        emit runFinished(true);
    }
    else
    {
        QString time = getCurrentTime();
        runOutput_ +=
                time + ": The process \"" + process_->program() +
                QString("\" exited with code %1.\n").arg(exitCode);
        runOutput_ += time + ": Test failed :-(\n";

        status_ = Status::RunError;
        emit runFinished(false);
    }
}
