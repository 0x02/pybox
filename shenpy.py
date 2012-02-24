class MsgColor:
    Header = '\033[95m'
    OkBlue = '\033[94m'
    OkGreen = '\033[92m'
    Warning = '\033[93m'
    Fail = '\033[91m'
    Endc = '\033[0m'

def HRSize(bytes):
    bytes = float(bytes)
    if bytes >= 1099511627776:
        terabytes = bytes / 1099511627776
        size = '%.2fT' % terabytes
    elif bytes >= 1073741824:
        gigabytes = bytes / 1073741824
        size = '%.2fG' % gigabytes
    elif bytes >= 1048576:
        megabytes = bytes / 1048576
        size = '%.2fM' % megabytes
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        size = '%.2fK' % kilobytes
    else:
        size = '%.2fb' % bytes
    return size
    
def DirSize(start_path):
	import os
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			try:
				fp = os.path.join(dirpath, f)
				total_size += os.path.getsize(fp)
			except:
				continue
	return total_size

def FileSize(path):
	import os
	if os.path.isdir(path):
		return DirSize(path)
	else:
		return os.path.getsize(path)

def ColPrint(table, space=1):
	import curses
	if not table:
		return

	colCount = curses.wrapper(lambda _: curses.tigetnum('cols'))
	colMaxWidth = []

	# Generate the colMaxWidth
	for line in table:
		for idx, col in enumerate(line):
			colw = len(col)
			if len(colMaxWidth) <= idx:
				colMaxWidth.append(colw)
			elif colw > colMaxWidth[idx]:
				colMaxWidth[idx] = colw

	for line in table:
		for idx, col in enumerate(line):
			colw = len(col)
			left = colMaxWidth[idx] - colw + space
			pad = ' ' * left
			print(col+pad, end='')
		print('')
