##  .:DieCast::
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

import random,math,pygame,sys,os,re
from common import *
try:
 import mixer_music
except:
 mixer_music=pygame.mixer.music
 
class Game:
        
        winstyle = 0 # pygame.FULLSCREEN
        resolution = (800,600)
        
        continue_msg = '(hit a key)'
        margin = 10
        frame_time = 40 ## 40 ms frames
        frame_time_ms = frame_time * .001
        delay = 500
        font_file = 'freesansbold.ttf'
        font_size = 14
        background = None
        
        color = BLACK
        bgcolor = WHITE
        title_color = BLACK
        
        def __init__(self):

          random.seed()
          
          pygame.init()
          if pygame.mixer:
           pygame.mixer.init()
          bestdepth = pygame.display.mode_ok(self.resolution, self.winstyle, 32)
          self.screen = pygame.display.set_mode(self.resolution, self.winstyle, bestdepth)
          
          if pygame.mixer and not pygame.mixer.get_init():
            print 'Warning, no sound'
            pygame.mixer = None
          
          self.Font = self.load_font(self.font_file,self.font_size)
          self.calibrate_font()
          self.images = dict_() #keep a cache of images used.
        
        def img_cache(self,name):
          if not self.images[name]:
            self.images[name] = load_image(name)
          return self.images[name]
        
        def msg_cache(self,msg,color):
          name = (msg,color)
          if not self.images[name]:
            self.images[name] = self.map.game.damage_font.render('%s'%msg,1,color)
          return self.images[name]
        
        def load_font(self,font_file,font_size):
          return pygame.font.Font(data(font_file),font_size)
        
        def calibrate_font(self):

          #get the height of a single line of text.
          self.text_height = self.Font.render('abcdefg',1,BLACK,WHITE).get_height() + 1
          self.text_width = self.Font.render('W',1,BLACK,WHITE).get_width() ## assume monospaced font.
          self.text_rows = (self.resolution[1]-2*self.margin) / self.text_height
          self.text_cols = (self.resolution[0]-2*self.margin) / self.text_width
          
        def quit(self):
          print "Bye."
          sys.exit(0)
          
        def pause(self,t):
          pygame.time.wait(int(t*self.delay))

        def wait_frame(self, num_frames = 1):
          'Wait for the passage of one frame in the game timeline.'
          pygame.time.wait(self.frame_time*num_frames)
           
        def get_key(self,t=BIG_NUM):
          T = time.time()
          while time.time() < T + t:
            for event in pygame.event.get():
              if (event.type == pygame.QUIT):
                  self.quit()
              elif (event.type == pygame.KEYDOWN):
                return event.key
            self.wait_frame()

        def wait_for_key(self,msg=''):
           self.text_line(msg+self.continue_msg,self.text_rows-1)
           self.disp()
           self.get_key()
           self.clear_text_line(self.text_rows-1)
  
        def cls(self):
          self.screen.fill(self.bgcolor)
          if self.background:
            self.screen.blit(self.background,(0,0))
            
        def disp(self):
          pygame.display.flip()
          
        def picture(self,name,pos=(0,0)):
          img = self.img_cache(name)
          if pos[0] + img.get_height() < self.screen.blit(img,pos):
            return pos[0]+img.get_height()
        
        def text_picture(self,name,line_num=0):
          return 1+self.picture(name,pos=(self.margin,self.margin+line_num*self.text_height))/self.text_height
  
        def text_line(self,msg,line_num = 0,color=None):
          if not color:
            color=self.color
            if msg[0:1] == '^':
              color = self.title_color
              msg = msg[1:]
          if line_num <= self.text_rows:
            self.render_text((self.margin,self.margin+self.text_height*line_num),msg,color,self.bgcolor)
            return line_num + 1
          else:
            return 0
  
        def text_pages(self,text):
          lines = text.split('\n')
          self.cls()
          i = 0
          for line in lines:
            if line[0:1] == '!':
              line_req = self.img_cache(line[1:]).get_height()/self.text_height
            else:
              line_req = 1
            
            if i + line_req >= self.text_rows:
              self.wait_for_key()
              self.disp()
              self.cls()
              i = 0
              
            if line[0:1] == '!':
              i = self.text_picture(line[1:],i)
            else:
              i = self.text_line(line,i)
          self.disp()
          self.wait_for_key()

        def menu(self,options,line_num = 0,callback = None):
          k = 0; y = 0
          while k != pygame.K_RETURN:
            for i in range(len(options)):
              self.text_line(" "+options[i]+"   ",line_num+i)
            self.text_line("<"+options[y]+">",line_num+y)
            self.disp()
            k = self.get_key(self.frame_time_ms)
            if k == pygame.K_DOWN:
              y += 1
            elif k == pygame.K_UP:
              y -= 1
            y = y % len(options)
            if callback:
              callback()
          return y

        def clear_text_line(self,line_num):
          self.text_line(2*' '*self.text_cols,line_num)
          
        def render_text(self,pos, text, color, bgcolor):
          textimg = self.Font.render(text, 1, color, bgcolor)
          self.screen.blit(textimg, pos)
          return pos[0] + textimg.get_width() + 5, pos[1] + textimg.get_height()

        def input_text(self, prompt = 'ENTER:', line_num = 0):
        
            k = 0
            s = prompt
            
            while k != pygame.K_RETURN:        
              if k == pygame.K_ESCAPE:
                  self.clear_text_line(line_num)
                  return None
              elif 123 > k > 47:
                  s += chr(k)
              elif k == pygame.K_BACKSPACE and len(s) > len(prompt):
                  s = s[:-1]
              cursorpos = self.text_line(s+"_  ",line_num)
              self.disp()
              k = self.get_key()
                
            self.clear_text_line(line_num)
            return s[len(prompt):]
          
        def play_music(self,file):
          if mixer_music:       
              musicfile = data('aud', file)
              mixer_music.load(musicfile)
              mixer_music.play(-1)
              
        def stop_music(self):
          if mixer_music:
              mixer_music.stop()
              
        def play(self):
          "this should be overridden."
          pass
