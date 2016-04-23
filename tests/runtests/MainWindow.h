#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QTextDocument>

class TestRunner;
class QPushButton;
class QTextEdit;

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
    QTextDocument textDocument_;
};

#endif // MAINWINDOW_H
