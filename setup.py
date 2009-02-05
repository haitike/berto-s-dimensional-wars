#  .:DieCast::
#  Author: echo85
#
#  GPL
#
#     This program is free software; you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation; version 2 of the License.
#   
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#
#  ADDENDUM REGARDING CODE QUALITY
#
#     This code is intended only to be run. Modifying is permitted but
#     not recommended, as I do not guarantee code quality. For the same
#     reason, I do not recommend using any code herein as an example
#     of correct coding practice or programming methodology. This notice
#     may be removed if I re-factor this project to better comply
#     with accepted programming practices.

from distutils.core import setup
import py2exe
import os


setup(console=['DC.py'])
setup(console=['DCedit.py'])

print os.popen(r'copy README.txt dist\README.txt').read()
print os.popen(r'copy README.txt dist\README_FIRST.txt').read()
print os.popen(r'mkdir dist\\save').read()
print os.popen('xcopy /S data\\* dist\\data\\*').read()
print os.popen(r'rename dist diecast_win').read()

print os.popen(r'mkdir dist').read()
print os.popen(r'copy README.txt dist\README.txt').read()
print os.popen(r'copy README.txt dist\README_FIRST.txt').read()
print os.popen(r'mkdir dist\\save').read()
print os.popen('xcopy /S data\\* dist\\data\\*').read()
print os.popen('xcopy *.py dist\\').read()
print os.popen(r'rename dist diecast_Src').read()
print os.popen(r'del dist\\setup.py').read()
