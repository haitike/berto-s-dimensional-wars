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

from common import *
from new import classobj
import pygame,random,math,re
import Diety

"""
Unit Module
===========
In data/units.csv, column #7, custom attributes are defined for various units.
In general, these override methods, but some have special meanings:

 range - the distance from which a target can be selected for a special ability
 time - the number of moves a unit must have to cast a special ability
 select - the shape of a selection boundary for special abilities

"""

SQUARE = "abs(L.x-tx) <= L.range and abs(L.y-ty) <= L.range"
CIRCLE = "abs(L.x-tx)**2 + abs(L.y-ty)**2 < (L.range+.3)**2"
DIAMOND = "abs(L.x-tx) + abs(L.y-ty) <= L.range"

ALL8 = "abs(L.x-tx) + abs(L.y-ty) > 0"
ONLY4 = "abs(L.x-tx) + abs(L.y-ty) == 1"

CURSOR,ARROW,MARKER = None,None,None  # user interativity graphics
U,Uord = {},[]
FLOOR,TREE,STONE,WATER,CHEST = None,None,None,None,None  # common map objects
FIREBALL = None # projectiles
ATTRS = ['name','hit','eva','mov','dmg','sta','abbrev']  # Unit attributes

EOT = 0
NO_MOVE = 1

class Tile:
        "A grid object requiring a single square."
        WIDTH=HEIGHT=32
        def __init__(self,m=None,x=0,y=0):
          self.map = m
          self.x,self.y = x,y
          for a in ATTRS:
            try:
              setattr(self,a, getattr(self,a+"_init") or getattr(self,a))
            except AttributeError:
              pass
        
        def draw(self,pic=None):
          self.map.game.screen.blit(pic or self.pic,(self.x*self.WIDTH,self.y*self.HEIGHT))
          if self.sta:
            hp = (self.WIDTH-4)*self.sta/self.__class__.sta
            if self.sta > .67 * self.__class__.sta: colour = GREEN
            elif self.sta > .34 * self.__class__.sta: colour = YELLOW
            else: colour = RED
            self.map.game.screen.fill(colour,(self.x*self.WIDTH+2,self.y*self.HEIGHT,hp,2))
        
        def flash(self,pic=None,duration=500):
          self.draw(pic)
          pygame.display.flip()
          self.draw()
          pygame.time.wait(duration)
          pygame.display.flip()
        
        def remove(self,replacewith = None):
          if not replacewith: replacewith = '.'
          self.map.set_draw(self.x,self.y,replacewith)
          pygame.display.flip()

class Movable(Tile): 
        "A Tile which may move."
        def __init__(self,*kw):
          Tile.__init__(self,*kw)
        
        def move(self,x,y):
          self.map.L[x][y] = self
          self.map.L[self.x][self.y] = FLOOR(self.map,self.x,self.y)
          self.map(self.x,self.y).draw()
          self.x = x
          self.y = y

          self.draw()
          pygame.display.flip()
    

class Unit(Movable):
        "A Movable which is controlled by one of the players."
        time = 0     # number of moves a special ability takes
        select = ""  # shape of target selection boundary
        range = 0    # distance of target selection boundary
        sleep = 0    # number of turns to skip (unless struck)
        stun = 0     # number of turns to skip
        memory = None
        
        def __init__(self,*kw):
          self.target = None
          Movable.__init__(self,*kw)
        
        def start(self):
            
            # decrement sleep and stun counters.
            if self.stun > 0:
                self.stun -= 1
                self.p("(stunned)")
                self.done()
            if self.sleep > 0:
                self.sleep -= 1
                self.p("(asleep)")
                self.done()
            # reorient self
            self.eva = self.__class__.eva
            
        def trmsg(self,msg):
            return msg.replace("$N",self.name).replace("$T","%s"%g(self.target,"name"))
        
        def p(self,msg,add=False,tmr=1):
            self.map.game.p(msg=self.trmsg(msg),add=add,tmr=tmr) 
            
        def reset(self,mov0 = 0):
            self.mov = mov0 or self.__class__.mov
            self.last_move = 0
            
        def march(self,x,y,mode=0):
          if abs(self.x-x)+abs(self.y-y) == 1:
            return self.move(x,y,mode)
          return NO_MOVE
           
        def move(self,x,y,mode=0):
          '''mode 0 - normal (intentional)
             mode 1 - test
             mode 2 - pushed'''

          self.target = self.map(x,y)
          kls = self.target.__class__
          
          if mode == 1: return kls
          
          if kls == FLOOR:
            if mode != 2: self.mov -= 1
            Movable.move(self,x,y)
          elif kls == TREE:
            self.chop()
          elif kls == CHEST:
            self.target.open(self)
            self.done()
          elif kls == STONE:
            self.pick()
          elif self.target_is_enemy():
            self.attack()
            
        def target_is_enemy(self):
            return self.target.__class__.race and self.target.__class__.race != self.race        
        
        def special(self):  ## this is meant to be overridden
            print self.name,"has no special abilities."
            
        def chop(self):
          self.p('chop, chop, chop... TIMBER!')
          self.target.remove()
          self.done()

        def pick(self):
          self.p('Despite your efforts, the rock does not budge.')

        def attack(self):
          self.target.target = self
          mark = 65 + self.hit - self.target.eva
          
          ## range deficiency
          rdef = int(((self.x-self.target.x)**2 + (self.y-self.target.y)**2 - 1)*6.0 / (self.range or 1))
          mark -= rdef
          
          acc = random.randint(0,99)
          # self.p("%s / %s"%(acc,mark))
          self.p("$N attacks $T. (%s%%)"%mark)
          
          if acc > mark:  ## dodge or miss
            miss = acc > mark + self.target.eva
            self.miss(miss)
            self.target.dodge(miss)
          else:
            self.strike()
          self.post_attack()
        
        def post_attack(self):
          "called after an attack"
          self.done()
        
        def dodge(self,miss):
          if not miss:
            self.p("$N dodged.",True,0)
            self.tile_msg("miss",YELLOW)
            self.eva -= 5
            
        def miss(self,miss):
          if miss:
            self.p("$N missed.",True,0) 
            self.target.tile_msg("miss",YELLOW)
            
        def strike(self):
          dmg = int(self.dmg[random.randint(0,len(self.dmg)-1)])
          self.target.absorb(dmg)
        
        def absorb(self,dmg):
          self.p("%s damage."%dmg,True,0)
        
          ## awaken sleeping units that are hit.
          if self.sleep > 0:
            self.sleep -= 1
            self.p("$N wakes up!")

          return self.hurt(dmg)
        
        def tile_msg(self,amt,color):
          for fade in [.4,.6,.8,1]:
            amount = self.map.game.msg_cache(amt,(color[0]*fade,color[1]*fade,color[2]*fade))
            self.draw(amount)
            pygame.display.flip()
            self.map.game.wait_frame(2)
          self.map.game.pause(.5)
          self.draw()
          
        
        def hurt(self,dmg):
          dmg = min(self.sta,dmg)
          self.tile_msg(dmg,RED)
          self.sta -= dmg
          if self.sta < 1:
            self.die()
          else:
            self.draw()
          return dmg # return the maximum damage
        
        def heal(self,sta):
          self.tile_msg(sta,WHITE)
          self.sta = min(self.__class__.sta,self.sta+sta)
        
        def die(self):
          self.p("$N has died.")
          self.target.kill()
          self.remove()
        
        def kill(self):
            pass
            
        def guard(self):  
          "called when turn is ended without action"
          self.done()
        
        def done(self):
          #self.p("$N is done.")
          self.draw()
          self.mov=0
          raise Diety.TurnOverException   

def FUNCTION(*args):
    return
FUNCTION = type(FUNCTION)

def set_chest_contents(self,contents):
          self.contents=contents
          
def open_chest(self,opener):

          if self.contents.abbrev==EVT_ACTION:
                self.contents.callback(opener)
          else:
                self.remove(self.contents.abbrev)
class Action:
        abbrev=EVT_ACTION
        def __init__(self,callback):
                self.callback=callback
##
## Helpers
##

#returns the tile past the target
def tile_past_target(self,factor = 1):
        tx = self.x+(self.target.x - self.x)+factor*sgn(self.target.x - self.x)
        ty = self.y+(self.target.y - self.y)+factor*sgn(self.target.y - self.y)
        if -1 < tx < self.map.WIDTH and -1 < ty < self.map.HEIGHT:
            return (tx,ty)

#################
## Unit methods
################

##chop methods
def eat_tree(self):
        self.heal(1)
        Unit.chop(self)

def jump_tree(self):
        T = tile_past_target(self)
        if self.map(T[0],T[1]).__class__==FLOOR:
            self.move(T[0],T[1])

##march methods
# these return information to the ai:
#   KLS - can move.
#   EOT - can move next turn if you stop.
#   NO_MOVE - can never move.

def march_all(self,x,y,mode=0):
        return self.move(x,y,mode)
            
def march_diag(self,x,y):
        if abs(x-self.x) == 1 == abs(y-self.y):
            return self.move(x,y)
        return NO_MOVE
            
def march_line(self,x,y):
        if x == self.x or y == self.y:
            if self.last_move and self.last_move != 10*(self.x-x)+self.y-y:
                return EOT
            self.last_move = 10*(self.x-x)+self.y-y
            return Unit.march(self,x,y)
        return EOT

def march_offline(self,x,y):
        if x == self.x or y == self.y:
            if self.last_move and self.last_move != 10*(self.x-x)+self.y-y:
                self.mov = min(self.mov,1)  
            else:
                self.last_move = 10*(self.x-x)+self.y-y
            return Unit.march(self,x,y)
        return EOT
            
##move methods
def timid_move(self,x,y,mode=0):
        self.target = self.map(x,y)
        if not self.target_is_enemy() or self.mov > 1:
            return Unit.move(self,x,y,mode)
        return EOT
            
def reckless_move(self,x,y,mode=0):
        self.target = self.map(x,y)
        if self.target_is_enemy() or self.mov > 1:
            return Unit.move(self,x,y,mode)
        return EOT

##die methods
def regenerate(self):
        if random.randint(1,self.chance_regenerate) > 1:
            Unit.die(self)
        else:
            self.p("$N regenerates.")
            self.sta = self.__class__.sta
            
def sprout(self):
        self.p("$N turned into a tree.")
        self.remove('*')
        
def morph(self):
        self.remove(self.morph_to)

##guard methods
def raise_shield(self):  
        self.shield = 1
        self.p('$N raises shield.')
        Unit.guard(self)

##strike methods
def drain(self):
        dmg = int(self.dmg[random.randint(0,len(self.dmg)-1)])

        self.p("(drain)",True)
        dmg = self.target.absorb(dmg)
        self.heal(dmg)
             
def sleep_strike(self):
        self.p("$T is stunned.",True)
        self.target.stun = 1
        Unit.strike(self)

def pushback(self):
        T = tile_past_target(self)
        if T and self.map(T[0],T[1]).__class__ == FLOOR:
          self.target.move(T[0],T[1])
          self.target = self.map(T[0],T[1])
          self.target.target = self
        Unit.strike(self)
        
##absorb methods
def spikes(self,dmg):
    self.p('$T get spiked.')
    self.target.absorb(1)
    return Unit.absorb(self,dmg)

def shield(self,dmg):
        if g(self,'shield'):
          self.p('$N blocks.',True,0)
          self.shield=0
          dmg-=1
        return Unit.absorb(self,dmg)

def rockskin(self,dmg):
        return Unit.absorb(self,max(dmg-1,0))

##dodge methods
def counterattack(self,miss):

        if not miss:
            # preserve actions
            self.attack()
            try:
                self.attack()
            finally:
                self.mov = m

##post_attack methods
def deduct_action(self):
    self.mov -= 2
    self.no_cancel = True

##special methods
def shoot(self):
        self.target = self.map.dieties[self.race].getTarget(self)
        if self.target_is_enemy():
            self.attack()
        else:
            raise Diety.CancelException

def snare(self):
        self.target = self.map.dieties[self.race].getTarget(self)
        if self.target.sta < random.randint(2,8):
          self.p('$T is is snared.')
          self.target.eva = 0
          self.target.hit = min(self.target.__class__.hit-15,self.target.hit)
        else:
          self.p('$T broke free of the snare.')
        self.done()

def smorph(self):
        self.remove(self.morph_to)
        raise Diety.TurnOverException
      
def revive(self):
        if self.sta == self.__class__.sta:
          smorph(self)
        else:
          self.heal(1)
        self.done()
        
def fireball(self):
        self.hurt(1)
        self.target = self.map.dieties[self.race].getTarget(self)
        dist = 0
        while self.target.__class__ == FLOOR and dist < 4:
            dist += 1
            self.target.flash(FIREBALL,500)
            T = tile_past_target(self)
            # end turn if fireball leaves screen
            if not T:
                self.done()
            else:
                self.target = self.map(T[0],T[1])
        if self.target_is_enemy():
            self.target.flash(FIREBALL,1000)
            self.target.absorb(random.randint(2,3))
            
        self.done()
            
##done methods
def lazy(self):
        if self.__class__.mov > self.mov:
            self.sleep = 1
        Unit.done(self)

def rest(self):
    
        self.heal(1)
        Unit.done(self)
##
## Tiles
##


def loadTiles(nx,ny,w,h,f):
    "returns a list of tiles from a file"
    T = []
    buf = load_image(f)
    for x in range (0,nx):
      for y in range (0,ny):
        T.append (buf.subsurface (x*w,y*h,w,h))
    return T

def generateUnits():
    global U,Uord,FLOOR,TREE,STONE,CHEST
    global CURSOR,ARROW,MARKER,FIREBALL
    T = loadTiles(10,7,32,32,"basictiles.gif")
    CURSOR,ARROW,MARKER = T[63:66]
    FIREBALL = T[56]
    Uord = []
    ## for each unit...
    for i,u in enumerate(readCsv(data("units.csv"))):
      ## build attribute dictionary
      def meval(a,b):
        if b in [1,2,3,5]:
            return eval(a)
        return a
      attrs = dict([(ATTRS[ii],meval(u[ii],ii)) for ii in range(7)])
      attrs['pic'] = T[i]
      attrs['race'] = g(Diety.RACE,int(i/7))
      for k,v in eval(u[7].replace(";",",")).items():
        if k in ATTRS:
          attrs[k+'_init']=v
        else:
          attrs[k]=v
          if k=='special':
            attrs['special_name'] = re.search("<function\s(.*?)\s",repr(v)).group(1) 

      ## generate the class for each unit
      
      U[u[0]] = U[u[6]] = classobj(u[0],((i<42 and Unit) or Movable,),attrs)
      
      Uord.append(U[u[0]])
      ## function delcaration 'foo':lambda self:'foo'
    FLOOR,TREE,STONE,WATER,CHEST = U['.'],U['*'],U['@'],U['#'],U['$']

    

 
