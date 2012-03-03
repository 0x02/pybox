#!/usr/bin/env python3.2

from spylib import *

def Usage():
    table = [['Usage:'],\
            ['', '-d, --dir=', 'Specify a dir.'],\
            ['', '-f, --file=', 'A text file contains paths.'],\
            ['', '-t, --to=', 'To which directory.'],\
            ['', '-h, --help', 'Show usage.']]

    ColPrint(table, 2)

def OnDirFilesError(oserror):
    print(oserror.filename + MsgColor.Warning + ' Permission denied!' + MsgColor.Endc)

def CheckFileAccess(fn, filepath):
    err = fn(filepath, dirisfile=False)
    if err == ErrFileAccess.Ok: 
        return True

    if err == ErrFileAccess.NotExist:
        print(filepath + MsgColor.Warning + ' File not exists!' + MsgColor.Endc)
    elif err == ErrFileAccess.PermDenied:
        print(filepath + MsgColor.Warning + ' Permission denied!' + MsgColor.Endc)
    elif err == ErrFileAccess.NotAFile:
        print(filepath + MsgColor.Warning + ' Not a txt file!' + MsgColor.Endc)

    return False

def CheckFileReadable(filepath):
    return CheckFileAccess(IsFileReadable, filepath)

def CheckFileWritable(filepath):
    return CheckFileAccess(IsFileWritable, filepath)

def ExpandAndVaildateOriginalPath(pathlist):
    import os
    # 1.Expand dir into path.
    expandedList = []
    for path in pathlist:
        if not os.path.isabs(path):
            print(path + MsgColor.Warning + ' Not abs path, ignored!' + MsgColor.Endc)
        elif os.path.isfile(path):
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

def PrepareOrCheckDestDir(todir):
    import os
    pathlist = None

    if os.path.exists(todir):
        print(MsgColor.OkGreen + 'Gathering dir info...' + MsgColor.Endc, end='')
        if os.path.isdir(todir) and os.access(todir, os.W_OK):
            pathlist = DirFiles(todir, OnDirFilesError)
            vaildlist = []
            for item in pathlist:
                if CheckFileWritable(item):
                    vaildlist.append(item)
            pathlist = vaildlist
            print(MsgColor.OkGreen + ' Done!', MsgColor.Endc)
        else:
            print(MsgColor.Fail + ' Failed!', MsgColor.Endc)
    else:
        print(MsgColor.Warning + 'Preparing dir...' + MsgColor.Endc, end='')
        try:
            os.mkdir(todir, 0o700)
            print(MsgColor.OkGreen + ' Done!', MsgColor.Endc)
            pathlist = []
        except:
            print(MsgColor.Fail + ' Failed!', MsgColor.Endc)

    return pathlist

def CalcFileHash(pathlist):
    hashlist = [Sha1File(item) for item in pathlist]
    return hashlist

def RmEmptyDirForFile(filename):
    import os
    checkparent = False
    dirname = os.path.dirname(filename)
    if len(dirname) > 0:
        try:
            os.rmdir(dirname)
            checkparent = True
        except:
            checkparent = False
    if checkparent:
        RmEmptyDirForFile(dirname)

def SyncCut(fromdir, newpathlist, todir):
    import os
    import shutil
    import uuid

    oldpathlist = PrepareOrCheckDestDir(todir)
    if oldpathlist == None:
        return
    
    print(MsgColor.OkGreen + 'Sync in cut mode...' + MsgColor.Endc)
    if len(oldpathlist) > 0:
        newhashlist = CalcFileHash(newpathlist);
        oldhashlist = CalcFileHash(oldpathlist)

        # 1.Ignore the unchanged files.(hash1=hash2, path1=path2)
        for idx in range(len(newhashlist)-1, -1, -1):
            newhash = newhashlist[idx]
            newpath = newpathlist[idx]
            dupidx = DupItemIndex(oldhashlist, newhash)
            for oldidx in dupidx:
                oldpath = oldpathlist[oldidx]
                topath = os.path.join(todir, newpath[len(fromdir):])
                if topath == oldpath:
                    del oldhashlist[oldidx]
                    del oldpathlist[oldidx]
                    del newhashlist[idx]
                    del newpathlist[idx]
                    break

        # 2.Merge the renamed files.(hash1=hash2, path1<>path2)
        #   Then ignore them!
        for idx in range(len(newhashlist)-1, -1, -1):
            newhash = newhashlist[idx]
            newpath = newpathlist[idx]
            if newhash in oldhashlist:
                oldidx = oldhashlist.index(newhash)
                oldpath = oldpathlist[oldidx]
                topath = os.path.join(todir, newpath[len(fromdir):])
                # If there is another file, let's rename it with a tmpname. 
                if topath in oldpathlist:
                    previdx = oldpathlist.index(topath)
                    tmppath = topath + '.' +uuid.uuid1().hex
                    print(MsgColor.OkGreen + '~ ' + MsgColor.Endc + os.path.relpath(tmppath))
                    shutil.move(topath, tmppath)
                    RmEmptyDirForFile(topath)
                    oldpathlist[previdx] = tmppath
                # Now we can mv the old file which has the same hash to our new path.
                print(MsgColor.OkGreen + '~ ' + MsgColor.Endc + os.path.relpath(topath))
                shutil.move(oldpath, topath)
                RmEmptyDirForFile(oldpath)
                del oldhashlist[oldidx]
                del oldpathlist[oldidx]
                del newhashlist[idx]
                del newpathlist[idx]

        # 3.Update content, then ignore them
        for idx in range(len(newhashlist)-1, -1, -1):
            newpath = newpathlist[idx]
            topath = os.path.join(todir, newpath[len(fromdir):])
            if topath in oldpathlist:
                oldidx = oldpathlist.index(topath)
                print(MsgColor.OkGreen + '! ' + MsgColor.Endc + os.path.relpath(topath))
                shutil.copy(newpath, topath)
                del oldhashlist[oldidx]
                del oldpathlist[oldidx]
                del newhashlist[idx]
                del newpathlist[idx]

        # Note: From now on, we won't maintain both two sides' hash/path lists!!!

        # 4.Add missing files according to the newpathlist.
        for item in newpathlist:
            topath = os.path.join(todir, item[len(fromdir):])
            print(MsgColor.OkGreen + '+ ' + MsgColor.Endc + os.path.relpath(topath), end='')
            try:
                os.makedirs(os.path.dirname(topath), 0o700, exist_ok=True)
                shutil.copyfile(item, topath)
                print()
            except:
                print(MsgColor.Fail + ' Failed!' + MsgColor.Endc)

        # 5.Clear files left in oldpathlist, they are all useless.
        for item in oldpathlist:
            print(MsgColor.OkGreen + '- ' + MsgColor.Endc + os.path.relpath(item))
            os.remove(item)
            RmEmptyDirForFile(item)
                
    else:
        # Directly copy from a to b.
        for item in newpathlist:
            topath = os.path.join(todir, item[len(fromdir):])
            print(MsgColor.OkGreen + '+ ' + MsgColor.Endc + os.path.relpath(topath), end='')
            try:
                os.makedirs(os.path.dirname(topath), 0o700, exist_ok=True)
                shutil.copyfile(item, topath)
                print()
            except:
                print(MsgColor.Fail + ' Failed!' + MsgColor.Endc)

def SyncWithDir(fromdir, todir):
    import os
    pathlist = ExpandAndVaildateOriginalPath([fromdir])
    SyncCut(fromdir+'/', pathlist, todir)

def SyncWithFile(textfile, todir):
    import os
    # Read path in a specified file.
    if not CheckFileReadable(textfile):
        print(MsgColor.Fail + 'Failed to sync!' + MsgColor.Endc)
        return

    print(MsgColor.OkGreen + 'Reading path list...' + MsgColor.Endc)
    pathlist = None
    with open(textfile, 'rt', encoding='utf-8') as f:
        pathlist = [line.strip() for line in f.readlines()]

    pathlist = ExpandAndVaildateOriginalPath(pathlist)

    SyncCut('/', pathlist, todir)

def main():
    import getopt
    import sys
    import os

    try:
        optval, args = getopt.getopt(sys.argv[1:], 'd:f:t:h', ['dir=', 'file=', 'to=', 'help'])
    except getopt.GetoptError as err:
        print(MsgColor.Fail + 'Invaild argv!' + MsgColor.Endc)
        Usage()
        sys.exit(2)

    if len(optval) > 2:
        print(MsgColor.Fail + 'Invaild argv!' + MsgColor.Endc)
        Usage()
        sys.exit(2)

    fromdir = None
    textfile = None
    todir = None
    for opt, val in optval:
        if opt in ('-d', '--dir') and val != '':
            fromdir = val
        elif opt in ('-f', '--file') and val != '':
            textfile = val
        elif opt in ('-t', '--to') and val != '':
            todir = val
        elif opt in ('-h', '--help'):
            Usage()
            sys.exit(0)
        else:
            print(MsgColor.Fail + 'Invaild argv!' + MsgColor.Endc)
            Usage()
            sys.exit(2)

    if todir != None:
        todir = os.path.abspath(todir)
        if fromdir != None:
            fromdir = os.path.abspath(fromdir)
            SyncWithDir(fromdir, todir)
        elif textfile != None:
            textfile = os.path.abspath(textfile)
            SyncWithFile(textfile, todir)

if __name__ == '__main__':
    main()
