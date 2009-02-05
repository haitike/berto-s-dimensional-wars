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

import pygame
import Game,Map,Units,Diety,random
from common import *

HELPTEXT = open('README.txt','r').read()

class Battle(Map.Map):
        def __init__(self,game,f,player_race,computer_race):
          Map.Map.__init__(self,game,f+".map.csv")
          self.f = f
          self.player_race=player_race
          self.computer_race=computer_race
          self.addPlayer(player_race,Diety.Player(game))
          self.addPlayer(computer_race,Diety.Computer(game))
          
        def clean(self):
          Map.Map.clean(self)
          if self.unit_count[self.player_race] < 1:
                raise(Map.LevelEnd(self.computer_race))
          if self.unit_count[self.computer_race] < 1:
                raise(Map.LevelEnd(self.player_race))

def win(race):
        def win_function(opener):
                raise(Map.LevelEnd(race))
        A = Units.Action(win_function)
        A.race = race
        return A

class Level(Battle):
        def __init__(self,game):
                Battle.__init__(self,game,self.title,self.player_race,self.computer_race)

class Level1(Level):
        title = "crowsbridge"
        player_race = "Puritan"
        computer_race = "Heretic"
        desc = """Your quest begins in a tranquil Puritan settlement.
Use the provided task force to save the town from the
Heretic foces who march from the bridge
and beware what may be hiding in the river bed.
!gun.gif"""
          
        def clean(self):
          Battle.clean(self)
          if self.day == 5:
                self.set_draw(5,11,'V')
                self.L[5][11].p("A vampire springs from the riverbed!")
                
class Level2(Level):
        title = "thicket"
        player_race = "Sylvan"
        computer_race = "Bedlam"
        desc = """When the Puritan elders become aware of the attack,
they activate a distant beacon intended to warn their ancient Sylvan
allies. The Sylvan awaken and acknowledge the warning but its signal
also attracts the attention of some nearby pirates, known as the
Bedlam. Protect the beacon from these riff-raff.

!ranger.gif"""
        def __init__(self,game):
          Level.__init__(self,game)
          TREASURE = [win('Bedlam')]
          self.bury_treasure(TREASURE)
          self.init_ai_memory()

class Level3(Level):
        ai_no_chop = True
        title = "jailbreak"
        player_race = "Dwarven"
        computer_race = "Heretic"
        desc = """Elsewhere in the world, three members of a gnomish clan named
the Terse sneak to rescue their people from enslavement in a
Heretic concentration camp. It becomes all too apparent to them
that the Heretic have hired or otherwise persuaded the
allegiance of the Bedlam.

!ooger_halfling.gif"""

        def __init__(self,game):
          Level.__init__(self,game)
          TREASURE = [self.U[a] for a in ['W','W','W','W','F','&','F','H']]
          self.bury_treasure(TREASURE)
          self.init_ai_memory()

class Level4(Level):
        title="desertstorm"
        player_race = "Bedouin"
        computer_race = "Bedlam"
        desc = """Despite their new found ally, the Bedlam explorations have
ventured too far from home into a vast desert hosted by the Bedouin.
"""

class DCGame(Game.Game):
        "Die Cast Game"
        winstyle=0
        map = None
        text_box_left = 595
        text_box_width = 190
        text_box_top = 400
        text_box_height = 178
        
        def menu_mode(self):
                self.color = RUST
                self.bgcolor = WHITE
                self.title_color = DARK_RUST
                self.Font = self.menu_font
                self.calibrate_font()
                self.background = self.menu_background
                self.play_music('beethoven7.ogg')
        
        def game_mode(self):
                self.color = GOLD
                self.bgcolor = BLACK
                self.Font = self.game_font
                self.calibrate_font()
                self.background = self.game_background
                self.stop_music()
        
        def __init__(self):
      
          Game.Game.__init__(self)
          self.menu_background = load_image('menu_bg.gif')
          self.game_background = load_image('dcgame_bg.gif')
          pygame.mouse.set_visible(0)
          self.game_font = self.load_font('LesserConcern.ttf',20)
          self.menu_font = self.load_font('LesserConcern.ttf',30)
          self.damage_font = self.load_font('freesansbold.ttf',12)
          self.TITLES = [load_image('title%s.gif'%i) for i in range(1,5)]
          self.flicker_timer = 200
          
        def calibrate_font(self):
          Game.Game.calibrate_font(self)
          self.text_box_cols = self.text_box_width/self.text_width
        
        def flicker(self):
          '''callback which animates the title.'''
          self.flicker_timer = (self.flicker_timer + 1) % random.randint(3,20)**2
          if self.flicker_timer <  4:
            self.screen.blit(self.TITLES[self.flicker_timer],(10,10))
          elif self.flicker_timer < 8:
            self.screen.blit(self.TITLES[7-self.flicker_timer],(10,10))
             
        def play(self):
          while 1:
            self.menu_mode()
            main_options = ['Campaigns','Load Custom Map','Help','Quit .:DieCast::']
            y = 2
            while y > 1:
              self.cls()
                
              self.picture('title1.gif',(10,10))
              y = self.menu(main_options,10,self.flicker)
              if y == 2:
                  self.text_pages(HELPTEXT)
              if y == 3:
                  self.quit()
                  
            self.line = 0
            if y == 0:
              self.play_campaign()
            if y == 1:
              self.play_custom()

        def play_custom(self):
          self.cls()

          while 1:
            f = self.input_text("   To what land dost thou venture: ")
            if not f: return
            if os.path.exists(os.path.join('data','maps',f+'.map.csv')):
              break
            else:
              self.cls()
              self.text_line("There exists no such land.",1)
          
          self.cls()
          cursor = self.text_picture('bowman_and_archer.gif')
          cursor = self.text_line("Choose race:", cursor)
          human_race = self.menu(Diety.RACE,cursor)
          
          self.cls()
          cursor = self.text_picture('goblin_ball.gif')
          cursor = self.text_line("Choose enemy race:", cursor)
          computer_race = self.menu(Diety.RACE,cursor)

          self.map = Battle(self,f,Diety.RACE[human_race],Diety.RACE[computer_race])
          self.game_mode()
          self.map.begin()
          
        def play_campaign(self):
          saved_games = [s[:-5] for s in os.listdir('save')]
          y = 0
          if saved_games:
            self.cls()
            cursor = self.text_picture('scroll.gif')
            cursor = self.text_line("^   Come hither and choose thy name: ",cursor)
            y = self.menu(saved_games+[' (NEW DIE CASTER)'],cursor)
          if y < len(saved_games):
            player_name = saved_games[y]
          elif y < 6:
            self.cls()
            cursor = self.text_line("^New Player")
            cursor = self.text_picture('soldierplan.gif',cursor)
            cursor = self.text_line("^Good morrow, Commander. I'll need your name for",cursor)
            cursor = self.text_line("^our records, should you perish in battle.",cursor)
            player_name = self.input_text("   I pray thee, sign thy name here: ",cursor)
            if not player_name: return
          
          f = os.path.join('save',player_name+'.save')
          if y == len(saved_games):
            open(f,'w').write('0')
            
          level = level_max = eval(open(f).read())
          MAPS = [Level1,Level2,Level3,Level4]
          
          while 1:
            self.cls()
            cursor = self.text_picture('goblin_ball.gif')
            cursor = self.text_line('^   Choose a level to play:',cursor)
            level = self.menu([m.title for i,m in enumerate(MAPS) if i <= level_max]+['QUIT GAME'],cursor)
            if level > level_max:
              print "All levels completed."
              self.quit()
            self.map = MAPS[level](self)
            self.text_pages("^"+self.map.title.upper()+"\n"+self.map.desc)
            try:
              self.game_mode()
              self.map.begin()
            except Map.LevelEnd,e:
              self.menu_mode()
              self.cls()
              if e.victor == self.map.player_race:
                self.play_music('bach.ogg')
                cursor = self.text_picture('victory.gif')
                cursor = self.text_line("You are victorious!",cursor)
                if level == level_max and level_max < len(MAPS)-1:
                  level_max += 1
                  cursor = self.text_line("Next level, %s is unlocked!"%MAPS[level_max].title,cursor)
                  open(f,'w').write('%s'%level_max)
                cursor = self.text_line('You won on turn %s.'%self.map.day,cursor)
                self.text_line('You had %s units remaining.'%self.map.unit_count[self.map.player_race],cursor)
                self.wait_for_key()
                self.stop_music()
              else:
                self.picture('death_image.gif')
                self.play_music('albioni.ogg')
                pygame.display.flip()
                self.pause(2)
                self.bgcolor = BLACK
                self.wait_for_key()
                self.bgcolor = WHITE
                self.stop_music()

        def p(self,msg="",tmr=1,add=False,color=GOLD,bgcolor=BLACK):
            "print a message in the text area"
            if not add:
              self.line = 0
              self.screen.fill(BLACK,(self.text_box_left,self.text_box_top,self.text_box_width,self.text_box_height))

            mx = self.text_box_left
            for w in msg.split(' '):
              textimg = self.Font.render(w+' ',1,color,bgcolor)
              if mx + textimg.get_width() > self.text_box_left+self.text_box_width:
                mx = self.text_box_left; self.line += 1
              self.screen.blit(textimg,(mx,self.text_box_top+self.line*self.text_height))
              mx += textimg.get_width()
            self.line += 1
            pygame.display.flip()
            self.get_key(self.delay*.001*tmr)
            
game = DCGame()
#game.playMusic('house_lo.wav')
game.play()
#game.stopMusic()
