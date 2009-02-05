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

import os,pygame,sys,time,string
#common utilities for other modules

GOLD = (200,160,0)
BLACK = (0,0,0)
WHITE = (255,255,255)
GREY  = (128,128,128)
RUST = (200,0,0)
DARK_RUST = (50,0,0)

GREEN = (0,225,0)
YELLOW = (225,225,0)
RED = (225,0,0)

AI_GOOD_SQUARES = 1
AI_BAD_SQUARES = 2
AI_QUEST_SQUARES = 4
AI_GO_SQUARES = AI_GOOD_SQUARES | AI_QUEST_SQUARES

MAP_HEIGHT = 18
MAP_WIDTH = 18

BIG_NUM = 10E10
DATA_DIR = 'data'

EVT_ACTION = 1

def data(*args):
    return os.path.join(DATA_DIR,*args)

def readCsv(f):
    return [m.strip().split(",") for m in open(f).readlines()]

def load_image(f):
    return pygame.image.load(data('img',f)).convert()

def g(d,k,default=None):
    if type(d) in (dict,list):
        try:
            return d[k]
        except (KeyError,IndexError):
            return default
    else:
        try:
            return getattr(d,k)
        except:
            return default

def sgn(i):
    if i > 0:
        return 1
    elif i == 0:
        return 0
    else:
        return -1

#CUSTOM DATA TYPES
class Nil:
    pass

class dict_(dict):
    """
    a dictionary with default values when key is not present.
    """
    def __init__(self,arg1=[],default=None):
       self.default = default
       dict.__init__(self,arg1)

    def __getitem__(self,key):
      try:
        return dict.__getitem__(self,key)
      except KeyError:
        return self.default

class list_(list):
    """ a list with subtraction defined and an 'add' method which is the same as
    append except when given the Nil object, which does nothing"""
    def add(self,item):
      if item != Nil: self.append(item)
    def __sub__(self,args):
      for arg in args:
        self.remove(arg)