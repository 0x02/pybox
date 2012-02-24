#!/usr/local/bin/python3.2

import sys
import os
import uuid
import time
import shutil
from shenpy import *

trash_max = 1024
trash_dir = os.path.expanduser('~/') + '.mytrash/'
item_content = 'content'
item_desc = 'desc'
desc_date = 'date '
desc_size = 'size '
desc_path = 'path '
desc_compressed = 'compressed '

# Print help.
def TrashHelp():
    info = '''Usage:
	-h	    Show this message.
	-s	    Show trash status.
	-l	    List all items in trash.
	-a	    Store items to its previous path.
	-r [1 2 n]  Restore items to its previous path.
	-z [1 2 n]  Compress items in trash.
	-Z [1 2 n]  Uncomprress items in trash.
	-d [1 2 n]  Delete items from trash.'''
    print(info)

# Init trash directory.
def trash_init():
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
	size = str(DirSize(trash_dir))
	print('Trash path:\t' + trash_dir)
	print('Trash size:\t' + HumanReadableSize(size))

# List items in trash.
def TrashList():
	print('NO.\t', 'Size\t', 'Date\t\t', 'Z ', 'From')

	items = os.listdir(trash_dir)
	for idx, item in enumerate(items):
		descPath = trash_dir + item + '/desc'
		desc = open(descPath, mode='r', encoding='utf-8')

		line = desc.readline().strip('\n')
		date = line[line.find(' '):]

		line = desc.readline().strip('\n')
		size = line[line.find(' '):]
		size = HumanReadableSize(size)

		line = desc.readline().strip('\n')
		oldPath = line[line.find(' '):]

		line = desc.readline().strip('\n')
		compressed = line[line.find(' '):]
		if bool(compressed):
			compressed = 'N'
		else:
			compressed = 'Y'

		desc.close()

		print(idx+1, '\t', \
				size, '\t', \
				date, '\t', \
				compressed, ' ', \
				oldPath)

# Delete items from trash.
def TrashDelete():
    pass

# Recycle the given item into trash.
def TrashStore(argvs):
	cwd = os.getcwd() + '/';
	for argv in argvs:
		oldPath = cwd + argv
		newDir = trash_dir + uuid.uuid1().hex + '/'
		contentDir = newDir + item_content
		
		if not (os.path.exists(oldPath)):
			print(MsgColor.Fail + 'File doesn\'t exists! ' + MsgColor.Endc + oldPath)
			continue

		if not (os.access(oldPath, os.W_OK)):
			print(MsgColor.Fail + 'Permission denied! ' + MsgColor.Endc + oldPath)
			continue

		print(MsgColor.OkGreen + 'Storing... ' + MsgColor.Endc + oldPath + \
			MsgColor.OkGreen + ' -> \n' + MsgColor.Endc + '\t' + newDir, end = '\t')

		os.mkdir(newDir, 0o700)
		os.mkdir(contentDir, 0o700)

		date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
		size = str(os.path.getsize(oldPath))

		desc = open(newDir + item_desc, mode='w', encoding='utf-8')
		desc.write(desc_date + date + '\n')
		desc.write(desc_size + size + '\n')
		desc.write(desc_path + oldPath + '\n')
		desc.write(desc_compressed + 'false\n')
		desc.close()

		shutil.move(oldPath, contentDir)

		print(MsgColor.OkGreen + 'size:' + MsgColor.Endc, HumanReadableSize(size))

# Restore items to its previous path.
def TrashRestore():
    desc = open()
    pass

# Compress items from trash.
def TrashCompress():
    pass

# Main Function
if not trash_init():
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
elif arg == '-a' and len(sys.argv) > 2:
	TrashStore(sys.argv[2:])
elif arg == '-r':
    TrashRestore()
elif arg == '-h':
    TrashHelp()
else:
    print(MsgColor.Fail + 'Bad arguments!' + MsgColor.Endc)
sys.exit(0)
