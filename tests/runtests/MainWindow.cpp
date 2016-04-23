#include "MainWindow.h"
#include "TestRunner.h"
#include "TestsTreeWidget.h"

#include <QPushButton>
#include <QTextEdit>
#include <QHBoxLayout>
#include <QFontDatabase>
#include <QSplitter>

#include <QtDebug>

namespace
{

// Thx to Kuba Ober! http://stackoverflow.com/questions/18896933/qt-qfont-selection-of-a-monospace-font-doesnt-work
bool isFixedPitch(const QFont & font)
{
    const QFontInfo fi(font);
    return fi.fixedPitch();
}

QFont getMonospaceFont()
{
    QFont font("monospace");
    font.setPixelSize(12);
    if (isFixedPitch(font)) return font;
    font.setStyleHint(QFont::Monospace);
    if (isFixedPitch(font)) return font;
    font.setStyleHint(QFont::TypeWriter);
    if (isFixedPitch(font)) return font;
    font.setFamily("courier");
    if (isFixedPitch(font)) return font;
    return font;
}

}

MainWindow::MainWindow()
{
    // Get some directory for testing
    // Later, these would would specified on the command line or via the interface
    QDir rootDir = QDir(QMAKE_PWD);
    while (rootDir.dirName() != "tests") // different number of cdUp() on Windows and Unix
        rootDir.cdUp();
    rootDir.cdUp();
    QDir unitDir = rootDir;
    unitDir.cd("tests");
    unitDir.cd("unit");

    QDir rootOutDir = QDir(QMAKE_OUT_PWD);
    while (rootOutDir.dirName() != "tests") // different number of cdUp() on Windows and Unix
        rootOutDir.cdUp();
    rootOutDir.cdUp();
    QDir unitOutDir = rootOutDir;
    unitOutDir.cd("tests");
    unitOutDir.mkdir("unit");
    unitOutDir.cd("unit");

    // Unit tests tree widget
    unitTestsTreeWidget_ = new TestsTreeWidget(unitDir, unitOutDir);

    /*

    // Test runner
    testRunner_ = new TestRunner(unitDir, unitOutDir, "tst_Bar.cpp", this);
    connect(testRunner_, &TestRunner::compileFinished, this, &MainWindow::onCompileFinished_);
    connect(testRunner_, &TestRunner::runFinished, this, &MainWindow::onRunFinished_);

    // Buttons
    compileButton_ = new QPushButton("Compile");
    runButton_ = new QPushButton("Run");
*/
    // Text Edit
    textDocument_.setDefaultFont(getMonospaceFont());
    textEdit_ = new QTextEdit();
    textEdit_->setDocument(&textDocument_);
    textEdit_->setReadOnly(true);

    QSplitter * splitter = new QSplitter();
    splitter->addWidget(unitTestsTreeWidget_);
    splitter->addWidget(textEdit_);
    splitter->setCollapsible(0, false);
    splitter->setCollapsible(1, false);
    setCentralWidget(splitter);

    // Compile on click
    //connect(compileButton_, &QPushButton::clicked, this, &MainWindow::onCompileButtonClicked_);
    //connect(runButton_, &QPushButton::clicked, this, &MainWindow::onRunButtonClicked_);
}

void MainWindow::onCompileButtonClicked_()
{
    textDocument_.setPlainText("");
    testRunner_->compile();
}

void MainWindow::onRunButtonClicked_()
{
    textDocument_.setPlainText("");
    testRunner_->run();
}

void MainWindow::onCompileFinished_()
{
    textDocument_.setPlainText(testRunner_->compileOutput());
}

void MainWindow::onRunFinished_()
{
    textDocument_.setPlainText(testRunner_->output());
}
