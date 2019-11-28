import sys
import os
import random
import errno
import shutil

num_to_grab = int(sys.argv[2])
output_dir_name = sys.argv[1].strip()
dir_to_grab_from = os.path.join(os.getcwd(), '..', 'log_extractor', 'intermediate_output', 'entries_by_session')
output_dir = os.path.join(os.getcwd(), output_dir_name)
try:
	os.makedirs(output_dir)
except OSError as e:
	if e.errno != errno.EEXIST:
		print("Operation failed: could not create write directory " + str(e))
		sys.exit()
for i in range(num_to_grab):
	filename = random.choice(os.listdir(dir_to_grab_from))
	shutil.copy(os.path.join(dir_to_grab_from, filename), output_dir)