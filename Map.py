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

import Diety,Units,pygame
from common import *
import ai

class LevelEnd:
        def __init__(self,victor):
          self.victor=victor
          
class Map:
        ai_no_chop = False # prevents AI from chopping trees (strategic)
        ## the number of sprites we can fit on the screen is WIDTH * HEIGHT        
        WIDTH = MAP_WIDTH; HEIGHT = MAP_HEIGHT
        unit_count={} # tally the number of units for each race.
        day = 0 # keep track of number of scans.
        
        def __init__(self,game,f):
          self.dieties = dict([(i,Diety.Computer(game)) for i in Diety.RACE])
          self.game = game
          self.Units = Units # an ugly hack to avoid circular imports

          Units.generateUnits()
          self.U=self.Units.U
          self.L = [[None]*self.HEIGHT for dummy in xrange(self.WIDTH)]
          self.M = [(x,y) for y in xrange(self.HEIGHT) for x in xrange(self.WIDTH)]
          if f:
            self.load(f)
        
        def begin(self):
          self.game.cls()
          self.draw()
          while 1: self.scan()
        
        def __call__(self,x,y):
            return self.L[x][y]
        
        def set_tile(self,x,y,abbrev):
          self.L[x][y] = self.U[abbrev](self,x,y)
        
        def set_draw(self,x,y,abbrev):
          self.set_tile(x,y,abbrev)
          self.L[x][y].draw()
        
        def load(self,f):
            for y,l in enumerate(open(data('maps',f)).readlines()):
              for x,u in enumerate(l.strip().split(",")):
                self.set_tile(y,x,u)

        def save(self,f):
            open(data('maps',f),'w').write( \
                '\n'.join([','.join([u.abbrev for u in l]) for l in self.L ]) )

        def draw(self):
          "draw entire map"
          for x,y in self.M:
              self.L[x][y].draw()
          pygame.display.flip()

        def clean(self):
          self.day += 1
          "resets move actions for a new scan and collects statistics."
          for race in Diety.RACE:
            self.unit_count[race] = 0

          for x,y in self.M:
            l = self.L[x][y]
            if l.race:
              self.unit_count[l.race] += 1
            self.L[x][y].mov = l.__class__.mov
              
        def init_ai_memory(self):
          '''automatically set up memory for ai controlled units.
          currently only contains logic for treasure chests.'''
          for race,diety in self.dieties.items():
           if diety.__class__ == Diety.Computer:
            mem = ai.Memory()
            for x,y in self.M:
              l = self.L[x][y]
              
              if l.__class__ == self.U['$']:
                if type(l.contents) == self.Units.Action:
                  if l.contents.race == race:
                    mem[(x,y)] = AI_QUEST_SQUARES
                else:
                  if l.contents.race == race:
                    mem[(x,y)] = AI_GOOD_SQUARES
                  else:
                    mem[(x,y)] = AI_BAD_SQUARES
                
            for x,y in self.M:
                l = self.L[x][y]
                if race == l.race:
                  self.L[l.x][l.y].memory = mem
          
        def _scan(self,l):
              if l.race:
                if l.mov:
                    self.dieties[l.race].turn(l)
                    
        def iterate(self,callback):
          for x,y in self.M:
                callback(self.L[x][y])

        def scan(self):
          "scan map for dieties' turn"
          self.clean()
          pygame.display.flip()
          self.iterate(self._scan)

        def bury_treasure(self,contents):
          "sets contents of treasure chests."
          i=0
          for x,y in self.M:
              if self.L[x][y].__class__ == self.U['$']:
                self.L[x][y].set_contents(contents[i%len(contents)])
                i+=1
        
        def addPlayer(self,race,player):
          self.dieties[race] = player
