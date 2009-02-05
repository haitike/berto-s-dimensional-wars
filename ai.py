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

from Units import *
from common import *
import time

RMOVES = [ (0,1),(0,-1),(1,0),(-1,0) ]
DMOVES = [ (-1,-1),(1,-1),(1,1),(-1,1) ]        
MOVES= RMOVES + DMOVES

class Ai:
    
    def __init__(self,g):
      self.game=g  
      self.SS = dict_()
      self.best_moves = list_()
      self.best_points = 0
      
    def search(self,L):
      "search for a move. L=None for test mode."
      global SS,best_moves,best_points
      
      #benchmarking
      start_time = time.time()
      num_iterations = 0
      
      self.SS = dict_()
      self.best_points = 0
      
      xx,yy=L.x,L.y
      self.L=L

      self.SS[(L.x,L.y)] = Pmove(self,(L.x,L.y),L.mov,points=0)
      self.best_moves = list_((self.SS[(L.x,L.y)],))      
      newM = list_()
      curM = list_()
      oldM = list_()

      for k in self.SS.keys():
        newM.add(k)

      while newM:
        #print curM
        oldM += curM
        curM = newM
        newM = list_()
        
        for m in curM:
          for move in MOVES:
           
            L.x,L.y = m
            if (-1 < L.x+move[0] < self.game.map.WIDTH and \
                 -1 < L.y+move[1] < self.game.map.HEIGHT):
                 
              num_iterations += 1
               
              mov = L.mov
              KLS = self.SS[m].step(move,L.march(L.x+move[0],L.y+move[1],True))
              L.mov = mov
              
              newM.add(KLS)
        
      oldM += curM
      L.x,L.y=xx,yy

      #for y in range(MAP_WIDTH):
      #  for x in range(MAP_WIDTH):
      #    print '%s%s'%(L.map(x,y).abbrev, self.SS[(x,y)] and self.SS[(x,y)].points or 0),
      #  print ''
      #      
      #print "time&iterations = ",time.time() - start_time, num_iterations
      return self.best_moves
      
class Memory(dict_):
    def __init__(self):
        dict_.__init__(self,[],0)
    QUEST_SQUARES = []
    "given to units to cache ai variables."
    def __setitem__(self,key,val):
        if val & AI_QUEST_SQUARES:
            self.QUEST_SQUARES.append(key)
        dict.__setitem__(self,key,val)

class Pmove:
    "possible move. branches off using a dynamic programming technique defined in Ai."
    def __init__(self,parent=None,coords=(0,0),agi=0,points=0):

      if parent.__class__ == Ai:
        self.ai = parent
        self.parent = None
      else:
        self.parent=parent
        self.ai=parent.ai
      self.agi=agi
      self.points=points
      self.coords=coords

    def step(self,move,tcls):
      """One step of the ai's dynamic programming algorithm.
            move - the proposed action from the currently explored state.
            tcls - class of targetted space."""

      l = self.ai.L
      cls = l.__class__
      agi = self.agi
      if tcls == NO_MOVE:
        return Nil
      elif tcls == EOT:
        agi = agi - (agi % cls.mov)

      agi -= 1
      
      if agi < -15:
        return Nil # cap the number of steps the ai takes.
      elif agi < -1 * l.mov:
        turn = 2 # (or subsequent turns)
      elif agi < 0:
        turn = 1
      else:
        turn = 0 # move is possible this turn.
        
      map = self.ai.game.map
      eot = False # end of turn flag
      eos = False # end of search flag
      
      tx,ty=self.coords[0]+move[0],self.coords[1]+move[1]
      tl=map(tx,ty)
      #print tx,ty,tl.abbrev,agi
      points = self.points - .1
      mem = (l.memory and l.memory[(tl.x,tl.y)]) or 0
      if l.race == tl.race:
        #print 'hit ally.'
        return Nil
      elif tl.race or mem & AI_GO_SQUARES:
        points += 10**(4-turn)
        if mem & AI_QUEST_SQUARES:
            points += 10**(5-turn)
        eot = True
        #print 'found',tl.name,'on turn',turn,'points',points

      if tl.abbrev in ['@','#']:
        #print 'hit rock.'
        return Nil
      elif tl.abbrev in ['*','$']:
        if tl.abbrev == '$' and mem & AI_BAD_SQUARES or tl.abbrev == '*' and map.ai_no_chop:
          return Nil
        eot = True
        
      if eot: agi = agi - ((agi % cls.mov) or cls.mov)
      
      if l.memory:
       for square in l.memory.QUEST_SQUARES:
        points += abs(l.x-square[0]) - abs(tx-square[0]) + abs(l.y-square[1]) - abs(ty-square[1])
       
      tile = self.ai.SS[(tx,ty)]
      
      if not tile or agi > tile.agi or (agi==tile.agi and points > tile.points):
        self.ai.SS[(tx,ty)] = Pmove(self,(tx,ty),agi,points)
        
        if points > self.ai.best_points:
          self.ai.best_points=points
          self.ai.best_moves=list_()
          
        if points >= self.ai.best_points:
          self.ai.best_moves.add(self.ai.SS[(tx,ty)])

        return (tx,ty)
      #print 'already exists.'
      return Nil