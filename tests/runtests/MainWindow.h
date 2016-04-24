#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTextDocument>

class TestRunner;
class TestsTreeWidget;

class QPushButton;
class QTextEdit;
class TestsTreeModel;

class MainWindow: public QMainWindow
{
    Q_OBJECT

public:
    MainWindow();

private slots:
    void onCompileButtonClicked_();
    void onRunButtonClicked_();

    void onCompileFinished_();
    void onRunFinished_();

private:
    TestRunner * testRunner_;
    QPushButton * compileButton_;
    QPushButton * runButton_;
    QTextEdit * textEdit_;
    TestsTreeWidget * unitTestsTreeWidget_;
    QTextDocument textDocument_;

    TestsTreeModel * unitTestsTreeModel_;
};

#endif // MAINWINDOW_H
