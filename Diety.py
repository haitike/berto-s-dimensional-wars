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

import pygame,ai,random
from common import *

RACE = ['Puritan','Sylvan','Bedouin','Bedlam','Heretic','Dwarven']

def p_k(k):
    return '%s'%getattr(pygame,'K_%s'%k)

#key bindings
KEY_MOVE = {}
for n,m in enumerate([None,(-1,1),(0,1),(1,1),(-1,0),None,(1,0),(-1,-1),(0,-1),(1,-1)]):
    KEY_MOVE[p_k('KP%s'%n)] = m
for n,m in enumerate([('COMMA','DOWN'),('j','LEFT'),('l','RIGHT'),('i','UP')]):
    KEY_MOVE[p_k(m[0])] = KEY_MOVE[p_k(m[1])] = KEY_MOVE[p_k("KP%s"%(n*2+2))]

KEY_DONE = [pygame.K_KP5,pygame.K_k]
KEY_CANCEL = [pygame.K_KP0,pygame.K_ESCAPE]
KEY_SPECIAL = [pygame.K_RETURN,pygame.K_KP_ENTER,pygame.K_SPACE]
KEY_QUIT = [pygame.K_q]
AI_MOVES = [v for v in KEY_MOVE.values() if v]

class Diety:  ## abstract base class
      def __init__(self,g):
        self.game = g
      def drawCursor(self,x,y):
              C = self.game.map.Units.CURSOR
              self.game.screen.blit(C,(C.get_width()*x,C.get_height()*y))
              pygame.display.flip()
              
      def drawArrow(self,x,y):
              C = self.game.map.Units.ARROW
              self.game.screen.blit(C,(C.get_width()*x,C.get_height()*y))
              pygame.display.flip()
                
class Player(Diety):
               
      def turn(self,L):
          # some identifier shortcuts
          try:
              mov0 = L.mov
              L.reset(mov0)
              L.start()
              xx,yy = L.x,L.y
              while 1:
                  L.p('$N (%s/%s) M: %s'%(L.sta,L.__class__.sta,L.mov),tmr=0)
                  self.drawCursor(L.x,L.y)
                  k = self.game.get_key()
                  
                  if k in KEY_QUIT:
                    self.game.quit()
                    
                  m = g(KEY_MOVE,str(k))
                  
                  if m and L.mov > 0:
                      tx,ty = L.x+m[0],L.y+m[1]
                      if -1 < tx < self.game.map.WIDTH and -1 < ty < self.game.map.HEIGHT:
                          L.march(tx,ty)
                          
                  if k in KEY_CANCEL and not g(L,"no_cancel"):
                      L.move(xx,yy)
                      L.reset(mov0)
                      self.drawCursor(L.x,L.y)
                  if k in KEY_SPECIAL and L.mov >= L.time:
                      try: # return to here if there's a cancel command
                          L.special()
                      except CancelException:
                          pygame.display.flip()
                  if k in KEY_DONE: L.guard()
                  
          except TurnOverException:
              pygame.display.flip()

      def getTarget(self,L):
          "L.select is a condition that is true when a given tile is a legal target"
          L.p(L.special_name)
          tx,ty = L.x,L.y # set target to origin
          while 1:
              self.drawArrow(tx,ty)
              pygame.display.flip()
              k = self.game.get_key()
              m = g(KEY_MOVE,str(k))
              txx,tyy = tx,ty
              if m: tx,ty = tx+m[0],ty+m[1]
              if not eval(L.select) and -1 < tx < self.game.map.WIDTH and -1 < ty < self.game.map.HEIGHT:
                  tx,ty = txx,tyy
              else:
                  self.game.map(txx,tyy).draw()
              if k in KEY_CANCEL:
                  self.game.map(txx,tyy).draw()
                  raise CancelException
              if k in KEY_SPECIAL: return self.game.map(tx,ty)

class Computer(Diety):
    def __init__(self,g,brain=None):
        self.brain=brain or ai.Ai(g)
        Diety.__init__(self,g)

    def turn(self,L):
      try:
        moves = self.brain.search(L)
        move = random.choice(moves)
        steps = []
        while move.parent.__class__ == ai.Pmove:
          steps.append(move.coords)
          move = move.parent
        steps.reverse()
        
        if len(steps): self.game.pause(.3)
        for step in steps:
          pygame.time.wait(self.game.delay/3)
          L.march(step[0],step[1])
          if L.mov < 1: break
        L.guard()
        
      except TurnOverException:
        pygame.display.flip()
        
    
class TurnOverException:
    pass

class CancelException:
    pass
    
