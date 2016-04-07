TEMPLATE = subdirs
CONFIG += ordered
SUBDIRS = src

#!isEmpty(BUILD_TESTS): SUBDIRS += tests
SUBDIRS += tests
