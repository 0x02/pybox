class MsgColor:
    Header = '\033[95m'
    OkBlue = '\033[94m'
    OkGreen = '\033[92m'
    Warning = '\033[93m'
    Fail = '\033[91m'
    Endc = '\033[0m'

def HumanReadableSize(bytes):
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
    
import os
def DirSize(start_path = '.'):
	total_size = 0
	for dirpath, dirnames, filenames in os.walk(start_path):
		for f in filenames:
			try:
				fp = os.path.join(dirpath, f)
				total_size += os.path.getsize(fp)
			except:
				continue
	return total_size
