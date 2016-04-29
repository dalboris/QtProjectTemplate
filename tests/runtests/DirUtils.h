#ifndef DIRUTILS_H
#define DIRUTILS_H

#include <QDir>
#include <QString>

/// \class DirUtils
/// \brief Convenient class to perform operations on directories
///
class DirUtils
{
public:
    /// Performs a cd operation on the dir. Reports if couldn't.
    /// Returns false if couldn't.
    ///
    static bool cd(QDir & dir, QString relPath);

    /// Performs a mkdir operation on the dir. Reports if couldn't.
    /// Returns false if couldn't.
    ///
    static bool mkdir(QDir & dir, QString name);

    /// Returns the distribution's root directory. Example:
    ///     /home/boris/Documents/QtProjectTemplate
    ///
    static QDir rootDir();

    /// Returns the distribution's root out directory. Example:
    ///     /home/boris/Documents/build-QtProjectTemplate-Desktop_Qt_5_5_1_GCC_64bit-Release
    ///
    static QDir rootOutDir();

    /// Returns the directory given by \p relPath, relative to rootDir()
    ///
    static QDir dir(const QString & relPath);

    /// Returns the out directory given by \p relPath, relative to outRootDir()
    ///
    static QDir outDir(const QString & relPath);
};

#endif // DIRUTILS_H
