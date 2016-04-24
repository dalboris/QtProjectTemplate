#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTextDocument>

class TestTreeModel;
class QTextEdit;

class MainWindow: public QMainWindow
{
    Q_OBJECT

public:
    MainWindow();

private:
    TestTreeModel * testTreeModel_;

    QTextDocument textDocument_;
    QTextEdit * textEdit_;
};

#endif // MAINWINDOW_H
