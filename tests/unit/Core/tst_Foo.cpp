#include "Test.h"
#include "Gui/Windows/MainWindow.h"

BEGIN_TESTS

void onePlusOneEqualsTwo()
{
    QCOMPARE(1+1, 2);

    Gui::MainWindow mw;
}

END_TESTS
