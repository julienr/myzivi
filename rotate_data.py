"""
Keep only N_TO_KEEP most recent files from _data
"""
import shutil
import os
import ziviscrap.settings as settings

N_TO_KEEP = 5

DATA_DIR = os.path.dirname(settings.DATA_DIR)
assert len(DATA_DIR) != 0

def sorted_ls(path):
	mtime = lambda f: os.stat(os.path.join(path, f)).st_mtime
	return list(sorted(os.listdir(path), key=mtime))

datadirs = sorted_ls(DATA_DIR)
to_delete = datadirs[:-N_TO_KEEP]

for d in to_delete:
	assert d.startswith('scraped_')
	print 'deleting : ', d
	shutil.rmtree(os.path.join(DATA_DIR, d))
