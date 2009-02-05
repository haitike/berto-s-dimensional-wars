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
import Game,Map,Units,Diety,sys
from common import *

KEY_SAVE = [pygame.K_s]
KEY_OPEN = [pygame.K_o]
KEY_QUIT = [pygame.K_q]

class DCEditor(Game.Game):
    "Die Cast Editor"
    color=WHITE
    bgcolor=BLACK
    margin=3
    def __init__(self):
        Game.Game.__init__(self)

    def play(self):

        ## configure the mouse
        #pygame.mouse.set_visible(1)
        pygame.mouse.set_cursor(*pygame.cursors.broken_x)

        self.map = Map.Map(self,"empty.map.csv")
        map = self.map
        map.draw()
        U = map.Units.Uord; i = 0
        # draw palette
        for u in U:
            u(map,19+i/14,i%14).draw()
            i+=1
        self.disp()
        
        PAINT = map.Units.U["."]
        down = 0; x,y = 0,0

        while 1:
            for event in pygame.event.get():
                # print event
                # handle the keys
                if event.type == pygame.KEYDOWN:
                    k = event.key
                    if k in KEY_SAVE:
                        f = self.input_text("Save File: ",self.text_rows-1)+".map.csv"
                        map.save(f)
                        self.wait_for_key(f+" saved. Hit a key to continue")

                    elif k in KEY_OPEN:
                        f = self.input_text("Open File: ",self.text_rows-1)+".map.csv"
                        map.load(f)
                        map.draw()
                        self.wait_for_key(f+" loaded.")
 
                    elif k in KEY_QUIT:
                        self.quit()
                   
                elif (event.type == pygame.QUIT):
                    self.quit()            
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    down = 1
                elif event.type == pygame.MOUSEBUTTONUP:
                    down = 0
                    
                x,y = pygame.mouse.get_pos()
                x/=32
                y/=32
                if down:

                    if x < 18 and y < 18:
                        map(x,y).remove(PAINT.abbrev)

                    elif x > 18:
                        try:
                          PAINT = U[(x-19)*14+y]
                        except IndexError:
                          pass
   
            self.text_line('%s,%s     '%(x,y),self.text_rows-1)
            self.disp()
            self.wait_frame()
        
game = DCEditor()
game.play()


