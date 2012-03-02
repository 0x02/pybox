#!/usr/bin/env python3.2

from spylib import *
def Usage():
	table = [['Usage:', 'synclist -f list -t ./dir'],\
			['', '-f, --from=', 'The list contains your target files.'],\
			['', '-t, --to=', 'To which directory.']]

	syplib.ColPrint(table, 2)

def OnDirFilesError(oserror):
	print(oserror.filename + MsgColor.Warning + ' Permission denied!' + MsgColor.Endc)

def CheckFileReadable(filepath, dirisfile=True):
	err = IsFileReadable(filepath, dirisfile=dirisfile)
	if err == ErrFileReadable.Ok: 
		return True

	if err == ErrFileReadable.NotExist:
		print(filepath + MsgColor.Warning + ' File not exists!' + MsgColor.Endc)
	elif err == ErrFileReadable.PermDenied:
		print(filepath + MsgColor.Warning + ' Permission denied!' + MsgColor.Endc)
	elif err == ErrFileReadable.NotAFile:
		print(filepath + MsgColor.Warning + ' Not a txt file!' + MsgColor.Endc)

	return False

def GetSrcList(fileList):
	import os
	# Read vaild src files from txt, expand dir into files.
	srcList = []
	with open(fileList, 'rt', encoding='utf-8') as f:
		for line in f.readlines():
			line = line.strip()
			if not CheckFileReadable(line):
				continue
		
			if os.path.isfile(line):
				srcList.append(line)
			elif os.path.isdir(line):
				srcList += DirFiles(line, OnDirFilesError)

	srcList.sort(key = KeySortPathLower)
	return srcList

def SyncList(fileList, toDir):
	import os

	if not CheckFileReadable(fileList, dirisfile=False):
		print(MsgColor.Fail + 'Failed to sync!' + MsgColor.Endc)
		return

	print(MsgColor.OkGreen + 'Reading file list...' + MsgColor.Endc)
	srcList = GetSrcList(fileList)

	if len(srcList) == 0:
		print(MsgColor.Warning + 'No file to sync!' + MsgColor.Endc)
		return

	print(MsgColor.OkGreen + 'Try sync them...' + MsgColor.Endc)
	for srcItem in srcList:
		print(srcItem)

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

	SyncList(fileList, toDir)

if __name__ == '__main__':
	main()
