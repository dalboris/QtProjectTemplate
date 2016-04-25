#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>

class TestTreeModel;
class TestItem;
class QModelIndex;
class OutputWidget;

class MainWindow: public QMainWindow
{
    Q_OBJECT

public:
    MainWindow();

private slots:
    void onTestItemActivated_(const QModelIndex & index);
    void onActiveItemOutputChanged_();

private:
    void updateOutput_();
    void setActiveTestItem_(TestItem * item);

private:
    TestTreeModel * testTreeModel_;
    TestItem * activeTestItem_;

    OutputWidget * relevantOutputWidget_;
    OutputWidget * compileOutputWidget_;
    OutputWidget * runOutputWidget_;
};

#endif // MAINWINDOW_H
