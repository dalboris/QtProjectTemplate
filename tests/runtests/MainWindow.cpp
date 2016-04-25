#include "MainWindow.h"
#include "TestItem.h"
#include "TestTreeModel.h"
#include "TestTreeView.h"
#include "OutputWidget.h"

#include <QTabWidget>
#include <QSplitter>
#include <QHeaderView>

MainWindow::MainWindow() :
    activeTestItem_(nullptr)
{
    // Get some directory for testing
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
    TestTreeView * testTreeView = new TestTreeView();
    testTreeView->setModel(testTreeModel_);
    testTreeView->header()->setDefaultAlignment(Qt::AlignCenter);
    testTreeView->header()->setStretchLastSection(false);
    testTreeView->header()->setSectionResizeMode(0, QHeaderView::Stretch);
    testTreeView->header()->setSectionResizeMode(1, QHeaderView::Fixed);
    testTreeView->header()->setSectionResizeMode(2, QHeaderView::Fixed);
    testTreeView->header()->resizeSection(1, 16);
    testTreeView->header()->resizeSection(2, 100);
    connect(testTreeView, &TestTreeView::activated, this, &MainWindow::onTestItemActivated_);

    // Output widgets
    relevantOutputWidget_ = new OutputWidget();
    compileOutputWidget_ = new OutputWidget();
    runOutputWidget_ = new OutputWidget();
    QTabWidget * outputWidgets = new QTabWidget();
    outputWidgets->addTab(relevantOutputWidget_, "Relevant Output");
    outputWidgets->addTab(compileOutputWidget_, "Compile Output");
    outputWidgets->addTab(runOutputWidget_, "Run Output");

    // Text Edit
    QSplitter * splitter = new QSplitter();
    splitter->addWidget(testTreeView);
    splitter->addWidget(outputWidgets);
    splitter->setCollapsible(0, false);
    splitter->setCollapsible(1, false);
    setCentralWidget(splitter);

    // More sensible default sizes and proportions
    resize(1200, 650);
    splitter->setStretchFactor(0,1);
    splitter->setStretchFactor(1,3);
}

void MainWindow::onTestItemActivated_(const QModelIndex & index)
{
    if (index.isValid())
        setActiveTestItem_(static_cast<TestItem*>(index.internalPointer()));
    else
        setActiveTestItem_(nullptr);
}

void MainWindow::setActiveTestItem_(TestItem * item)
{
    if (item != activeTestItem_)
    {
        if (activeTestItem_)
            activeTestItem_->disconnect(this);

        activeTestItem_ = item;

        if (activeTestItem_)
            connect(activeTestItem_, &TestItem::outputChanged,
                    this, &MainWindow::onActiveItemOutputChanged_);

        updateOutput_();
    }
}

void MainWindow::onActiveItemOutputChanged_()
{
    updateOutput_();
}

void MainWindow::updateOutput_()
{
    if (activeTestItem_)
    {
        relevantOutputWidget_->setOutput(activeTestItem_->output());
        compileOutputWidget_->setOutput(activeTestItem_->compileOutput());
        runOutputWidget_->setOutput(activeTestItem_->runOutput());
    }
    else
    {
        relevantOutputWidget_->setOutput("");
        compileOutputWidget_->setOutput("");
        runOutputWidget_->setOutput("");
    }
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
