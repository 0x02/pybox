#!/usr/local/bin/python3.2

import sys
import os
import uuid
import time
import shutil
import string
from shenpy import *

trash_max = 1024
trash_dir = os.path.expanduser('~/') + 'MyTrash' + '/'
item_content = 'content'
item_desc = 'desc'
desc_date = 'date '
desc_size = 'size '
desc_path = 'path '
desc_compressed = 'compressed '

# Print help.
def TrashHelp():
	table = [['Usage:'],\
			['', '-h', 'Show this message.'],\
			['', '-s', 'Show trash status.'],\
			['', '-l', 'List all items in trash.'],\
			['', '-a', 'Store items to trash.'],\
			['', '-r [1 2 n] -t [path]', 'Restore items.'],\
			['', '-d [1 2 n]', 'Delete items from trash.'],\
			['', '-c', 'Delete all items in trash.'],\
			['', '-z [1 2 n]', 'Compress items in trash.'],\
			['', '-Z [1 2 n]', 'Uncomprress items in trash.']]

	ColPrint(table)

# Init trash directory.
def TrashInit():
	if os.path.isdir(trash_dir) and os.access(trash_dir, os.W_OK):
		return True

	print(MsgColor.Warning + "Initializing trash dir..." + MsgColor.Endc, end = '')
	try:
		os.mkdir(trash_dir, 0o700)
		print(MsgColor.OkGreen + 'Done!', MsgColor.Endc)
		return True
	except:
		print(MsgColor.Fail + 'Failed!', MsgColor.Endc)
		return False

# Show trash status.
def TrashStatus():
	size = str(FileSize(trash_dir))
	table = [['Trash path:', trash_dir],\
			['Trash size:', HRSize(size)]]
	ColPrint(table)

	TrashList()

# List items in trash.
def TrashList():
	items = os.listdir(trash_dir)
	index = []
	for idx, item in enumerate(items):
		index.append(idx)
	TrashDoList(index)

def TrashDoList(index):
	table = [['NO.', 'Name', 'Size', 'Date', 'Z', 'From']]

	items = os.listdir(trash_dir)
	for idx, item in enumerate(items):
		if idx not in index:
			continue

		itemDir = trash_dir + item + '/'
		contentDir = itemDir + item_content + '/'

		name = os.listdir(contentDir)[0]

		descPath = itemDir + item_desc
		desc = open(descPath, mode='r', encoding='utf-8')

		line = desc.readline().strip('\n')
		date = line[line.find(' ')+1:]

		line = desc.readline().strip('\n')
		size = line[line.find(' ')+1:]
		size = HRSize(size)

		line = desc.readline().strip('\n')
		oldDir = line[line.find(' ')+1:]

		line = desc.readline().strip('\n')
		compressed = line[line.find(' ')+1:]
		if compressed.lower() == 'true':
			compressed = 'Y'
		else:
			compressed = 'N'

		desc.close()

		cols = [str(idx+1), name, size, date, compressed, oldDir]
		table.append(cols)

	ColPrint(table, 2, [1, 1, 2, 1, 1, 1])

# Recycle the given item into trash.
def TrashStore(argvs):
	for argv in argvs:
		oldPath = os.path.abspath(argv)
		oldDir = os.path.dirname(oldPath) + '/'
		newDir = trash_dir + uuid.uuid1().hex + '/'
		contentDir = newDir + item_content
		
		if not (os.path.exists(oldPath)):
			print(MsgColor.Fail + 'File doesn\'t exists! ' + MsgColor.Endc + oldPath)
			continue

		if not (os.access(oldPath, os.W_OK)):
			print(MsgColor.Fail + 'Permission denied! ' + MsgColor.Endc + oldPath)
			continue

		print(oldPath + \
				MsgColor.OkGreen + ' -> ' + MsgColor.Endc + \
				newDir, end = ' ')

		os.mkdir(newDir, 0o700)
		os.mkdir(contentDir, 0o700)

		date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		size = str(FileSize(oldPath))

		desc = open(newDir + item_desc, mode='w', encoding='utf-8')
		desc.write(desc_date + date + '\n')
		desc.write(desc_size + size + '\n')
		desc.write(desc_path + oldDir + '\n')
		desc.write(desc_compressed + 'false\n')
		desc.close()

		shutil.move(oldPath, contentDir)

		print(MsgColor.OkGreen + 'size:' + MsgColor.Endc, HRSize(size))

# Restore items.
def TrashRestore(argvs):
	items = os.listdir(trash_dir)

	index = []
	toPath = ''
	for idx, strIdx in enumerate(argvs):
		if strIdx == '-t' and len(argvs) > idx+1:
			toPath = argvs[idx+1]
			break

		if strIdx.isdigit() and int(strIdx) <= len(items) and int(strIdx) > 0:
			index.append(int(strIdx)-1)
			continue
	index.sort()
	if len(index) <= 0:
		return

	print(os.path.abspath(toPath))

	TrashDoList(index)
	if not TrashConfirm():
		return

	for idx, item in enumerate(items):
		if idx not in index:
			continue

		itemDir = trash_dir + item + '/'
		contentDir = itemDir + item_content + '/'
		descPath = itemDir + item_desc

		name = os.listdir(contentDir)[0]

		desc = open(descPath, mode='r', encoding='utf-8')

		line = desc.readline().strip('\n')
		line = desc.readline().strip('\n')
		line = desc.readline().strip('\n')
		oldDir = line[line.find(' ')+1:]

		line = desc.readline().strip('\n')
		#compressed = line[line.find(' ')+1:]
		#if compressed.lower() == 'true':

		desc.close()

		destDir = oldDir
		if len(toPath) != 0:
			destDir= os.path.abspath(toPath) + '/'
		if (os.path.isdir(destDir) and not os.access(destDir, os.W_OK)) or \
				os.path.isfile(destDir):
			print(MsgColor.Fail + 'NO.' + str(idx+1) + ' Invaild destination!' + MsgColor.Endc)
			continue
		if os.path.exists(destDir+name):
			print(MsgColor.Fail + 'NO.' + str(idx+1) + ' File already exists!' + MsgColor.Endc)
			continue

		if not os.path.exists(destDir):
			print(MsgColor.Warning + 'Preparing the destination dir...' + MsgColor.Endc)
			os.makedirs(destDir)

		shutil.move(contentDir+name, destDir+name)
		os.rmdir(contentDir)
		os.remove(descPath)
		os.rmdir(itemDir)
		print(MsgColor.OkGreen + 'NO.' + str(idx+1) + ' Done!' + MsgColor.Endc)

# Delete items from trash.
def TrashDelete(argvs):
	items = os.listdir(trash_dir)
	index = []
	for strIdx in argvs:
		if strIdx.isdigit() and int(strIdx) <= len(items) and int(strIdx) > 0:
			index.append(int(strIdx)-1)
			continue
	index.sort()
	if len(index) <= 0:
		return

	TrashDoList(index)
	if not TrashConfirm():
		return

	TrashDoDelete(index)

def TrashDoDelete(index):
	items = os.listdir(trash_dir)
	for idx, item in enumerate(items):
		if idx not in index:
			continue

		itemDir = trash_dir + item + '/'
		shutil.rmtree(itemDir)

		print(MsgColor.OkGreen + 'NO.' + str(idx+1) + ' Done!' + MsgColor.Endc)

# Clear items in trash.
def TrashClear():
	items = os.listdir(trash_dir)
	index = []
	for idx, items in enumerate(items):
		index.append(idx)

	TrashDoList(index)
	if not TrashConfirm():
		return

	TrashDoDelete(index)

# Compress items from trash.
def TrashCompress():
    pass

def TrashConfirm():
	accept = input('Accept? [y/n] ')
	if accept.lower() not in ['y', 'yes']:
		print(MsgColor.Warning + 'Operation was abandoned.' + MsgColor.Endc)
		return False
	else:
		return True

# Main Function
if not TrashInit():
	print(MsgColor.Fail + 'Could not initialize trash!' + MsgColor.Endc)
	sys.exit(-1)

if len(sys.argv) < 2:
    print(MsgColor.Fail + 'Need arguments!' + MsgColor.Endc) 
    TrashHelp()
    sys.exit(-1)

arg = sys.argv[1]
if arg == '-s':
    TrashStatus()
elif arg == '-l':
    TrashList()
elif arg == '-c':
	TrashClear()
elif len(sys.argv) > 2:
	if arg == '-a':
		TrashStore(sys.argv[2:])
	elif arg == '-r':
		TrashRestore(sys.argv[2:])
	elif arg == '-d':
		TrashDelete(sys.argv[2:])
elif arg == '-h':
    TrashHelp()
else:
    print(MsgColor.Fail + 'Bad arguments!' + MsgColor.Endc)
sys.exit(0)
