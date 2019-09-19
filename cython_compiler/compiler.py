# Copyright: NIcklasMCHD
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, version 3 of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see https://github.com/LuciaSoftware/lucia/blob/master/LICENSE.

import argparse
import hashlib
import json
import os
import subprocess
import sys
import platform 

def calculate_sha256(filename, block_size=2**20):
	"""Returns sha256 checksum for given file.
	Modified from: https://gist.github.com/juusimaa/5846242
	"""
	sha256 = hashlib.sha256()
	try:
		file = open(filename, 'rb')
		while True:
			data = file.read(block_size)
			if not data:
				break
			sha256.update(data)
	except IOError:
		print('File \'' + filename + '\' not found!')
		return None
	except:
		return None
	return sha256.hexdigest()

def _run_command(cmd):
	process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=sys.stderr)
	process.communicate()
	return process.wait()

def do_cythonization(args):
	print("Updating cythonize packages...")
	code = []
	hashchain = {}
	if os.path.isfile(platform.system() + ".hashchain"):
		sys.stdout.write("HashChain found, Loading ")
		sys.stdout.flush()
		hashchain = json.load(open(platform.system() + ".hashchain", "r"))
		sys.stdout.write("Loaded.\n")
	for path, subdirs, files in os.walk(os.getcwd()):
		for name in files:
			p = os.path.join(path, name)
			niceName = p[1+len(os.getcwd()):].replace("\\", "/")
			if "__" in niceName:
				continue
			if niceName == args.entry:
				sys.stdout.write(f"Skipping {niceName} because it is the entry to the application.\n")
				sys.stdout.flush()
				continue
			if niceName in sys.argv[0]:
				continue
			if niceName.lower().endswith(".py") == False:
				continue
			f = open(p, "r")
			data = f.read()
			f.close()
			code.extend(data.split("\n"))
			if p in hashchain:
				if hashchain[p] == calculate_sha256(p):
					continue
			sys.stdout.write("Cythonizing " + niceName)
			sys.stdout.flush()
			while True:
				status_code = _run_command(["cythonize", "--3str", "-i", niceName])
				if status_code < 0:
					sys.stdout.write("\nError cythonizing {}.\n{}\nWill try again.\n".format(niceName, status_code))
					sys.stdout.write(str(status_code))
					sys.stdout.write("\n")
					sys.stdout.flush()
					continue
				if status_code >= 0:
					hashchain[p] = calculate_sha256(p)
					sys.stdout.write("Done\n")
					sys.stdout.flush()
					break
	sys.stdout.write("Cythonized packages updated.\n")
	sys.stdout.flush()
	sys.stdout.write("Removing C files ")
	sys.stdout.flush()
	for path, subdirs, files in os.walk(os.getcwd()):
		for name in files:
			p = os.path.join(path, name)
			niceName = p[1+len(os.getcwd()):].replace("\\", "/")
			if niceName.lower().endswith(".c"):
				os.remove(p)
	sys.stdout.write("done\n")
	sys.stdout.flush()
	sys.stdout.write("Assembling imports ")
	sys.stdout.flush()
	imports = []
	for imp in code:
		if imp.startswith("import") or imp.startswith("from "):
			imports.append(imp)
	data = "# Import this file into your python entrypoint to get PyInstaller to recognize the imports required by your program.\n"
	for imp in imports:
		if imp in data.splitlines(): # if the import is idential to one already added.
			continue
		data += imp + "\n"
	f = open("__required_imports__.py", "w")
	f.write(data)
	f.close()
	sys.stdout.write("Done\n")
	sys.stdout.flush()
	sys.stdout.write("Saving HashChain ")
	json.dump(hashchain, open(platform.system() + ".hashchain", "w"))
	sys.stdout.write("Done\n")
	sys.stdout.flush()

def do_cythonization_removal(args):
	sys.stdout.write("Removing C files ")
	sys.stdout.flush()
	for path, subdirs, files in os.walk(os.getcwd()):
		for name in files:
			p = os.path.join(path, name)
			niceName = p[1+len(os.getcwd()):].replace("\\", "/")
			if niceName.lower().endswith(".c"):
				os.remove(p)
	sys.stdout.write("done\n")
	sys.stdout.flush()
	sys.stdout.write("Removing all .pyd files from the current project ")
	sys.stdout.flush()
	for path, subdirs, files in os.walk(os.getcwd()):
		for name in files:
			p = os.path.join(path, name)
			niceName = p[1+len(os.getcwd()):].replace("\\", "/")
			if niceName.lower().endswith(".pyd"):
				os.remove(p)
	sys.stdout.write("Done\n")
	sys.stdout.flush()
	sys.stdout.write("Removing HashChain ")
	sys.stdout.flush()
	try:
		os.remove(platform.system() + ".hashchain")
		sys.stdout.write("done\n")
		sys.stdout.flush()
	except:
		sys.stdout.write("No HashChain found.\n")
		sys.stdout.flush()

def main():
	parser = argparse.ArgumentParser(description="Cythonize your entire project while keeping the easyness of packaging with PyInstaller and testing with an interpreted language.")
	parser.add_argument("-c", "--cythonize", help="Cythonize your project and assemble imports.", default=False, action="store_true")
	parser.add_argument("-r", "--remove", help="Remove the .pyd files, so you can test with python.", default=False, action="store_true")
	parser.add_argument("-e", "--entry", help="The entry file that starts the program when ran with python. This file will not be cythonized", default=None)
	args = parser.parse_args()
	if args.cythonize == False and args.remove == False:
		parser.error("at least one of \"-c\" and ---\"-r\" is required.")
		sys.exit()
	if args.cythonize == True and args.entry is None:
		parser.error("When using the \"-c\" flag, entry must be set. If you don't have / need an entry point (or you're cythonizing a module), set the entry to \"_\".")
		sys.exit()
	if args.remove:
		do_cythonization_removal(args)
	if args.cythonize:
		do_cythonization(args)

if __name__ == "__main__":
	main()
