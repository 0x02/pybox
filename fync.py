#!/usr/bin/env python3.2

from spylib import *

def Usage():
    table = [['Usage:', 'synclist -f list -t ./dir'],\
            ['', '-f, --from=', 'The list contains your target files.'],\
            ['', '-t, --to=', 'To which directory.']]

    syplib.ColPrint(table, 2)

def OnDirFilesError(oserror):
    print(oserror.filename + MsgColor.Warning + ' Permission denied!' + MsgColor.Endc)

def CheckFileReadable(filepath):
    err = IsFileReadable(filepath, dirisfile=False)
    if err == ErrFileReadable.Ok: 
        return True

    if err == ErrFileReadable.NotExist:
        print(filepath + MsgColor.Warning + ' File not exists!' + MsgColor.Endc)
    elif err == ErrFileReadable.PermDenied:
        print(filepath + MsgColor.Warning + ' Permission denied!' + MsgColor.Endc)
    elif err == ErrFileReadable.NotAFile:
        print(filepath + MsgColor.Warning + ' Not a txt file!' + MsgColor.Endc)

    return False

def ExpandAndVaildatePath(pathlist):
    import os
    # 1.Expand dir into path.
    expandedList = []
    for path in pathlist:
        if os.path.isfile(path):
            expandedList.append(path)
        elif os.path.isdir(path):
            expandedList += DirFiles(path, OnDirFilesError)

    # 2.Remove duplicate path.
    expandedList = [item for item in set(expandedList)]

    # 3.Remove inaccessible path.
    vaildList = []
    for path in expandedList:
        if CheckFileReadable(path):
            vaildList.append(path)

    # 4.Sort list.
    vaildList.sort(key = KeySortPathLower)
    return vaildList

def SyncCut(pathlist, toDir):
    print(MsgColor.OkGreen + 'Sync in cut mode...' + MsgColor.Endc)
    for item in pathlist:
        print(item)

def SyncWithCli(pathlist, toDir):
    pass

def SyncWithFile(textfile, toDir):
    import os
    # Read path in a specified file.
    if not CheckFileReadable(textfile):
        print(MsgColor.Fail + 'Failed to sync!' + MsgColor.Endc)
        return

    print(MsgColor.OkGreen + 'Reading path list...' + MsgColor.Endc)
    pathlist = None
    with open(textfile, 'rt', encoding='utf-8') as f:
        pathlist = [line.strip() for line in f.readlines()]

    pathlist = ExpandAndVaildatePath(pathlist)

    if len(pathlist) == 0:
        print(MsgColor.Warning + 'Nothing to sync!' + MsgColor.Endc)
        return

    SyncCut(pathlist, toDir)

def main():
    import getopt
    import sys

    try:
        optval, args = getopt.getopt(sys.argv[1:], 'f:t:', ['file=', 'to='])
    except getopt.GetoptError as err:
        print(MsgColor.Fail + 'Invaild argv!' + MsgColor.Endc)
        Usage()
        sys.exit(2)

    if len(optval) != 2:
        print(MsgColor.Fail + 'Invaild argv!' + MsgColor.Endc)
        Usage()
        sys.exit(2)

    fileList = None
    toDir = None
    for opt, val in optval:
        if opt in ('-f', '--file') and val != '':
            fileList = val
        elif opt in ('-t', '--to') and val != '':
            toDir = val
        else:
            print(MsgColor.Fail + 'Invaild argv!' + MsgColor.Endc)
            Usage()
            sys.exit(2)

    SyncWithFile(fileList, toDir)

if __name__ == '__main__':
    main()
