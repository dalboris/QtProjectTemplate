#include "MainWindow.h"
#include "TestTreeModel.h"
#include "TestTreeView.h"

#include <QTextEdit>
#include <QFontDatabase>
#include <QSplitter>
#include <QHeaderView>

namespace
{

// Thx to Kuba Ober: http://stackoverflow.com/questions/18896933/qt-qfont-selection-of-a-monospace-font-doesnt-work
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

    // Unit tests tree
    testTreeModel_ = new TestTreeModel(unitDir, unitOutDir, this);
    TestTreeView * unitTestsTreeView = new TestTreeView();
    unitTestsTreeView->setModel(testTreeModel_);
    unitTestsTreeView->header()->setDefaultAlignment(Qt::AlignCenter);
    unitTestsTreeView->header()->setStretchLastSection(false);
    unitTestsTreeView->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    unitTestsTreeView->header()->setSectionResizeMode(1, QHeaderView::Fixed);
    unitTestsTreeView->header()->setSectionResizeMode(2, QHeaderView::Fixed);
    unitTestsTreeView->header()->resizeSection(1, 16);
    unitTestsTreeView->header()->resizeSection(2, 100);

    // Text Edit
    textDocument_.setDefaultFont(getMonospaceFont());
    textEdit_ = new QTextEdit();
    textEdit_->setDocument(&textDocument_);
    textEdit_->setReadOnly(true);

    QSplitter * splitter = new QSplitter();
    //splitter->addWidget(unitTestsTreeWidget_);
    splitter->addWidget(unitTestsTreeView);
    splitter->addWidget(textEdit_);
    splitter->setCollapsible(0, false);
    splitter->setCollapsible(1, false);
    setCentralWidget(splitter);
}

/*
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
*/
