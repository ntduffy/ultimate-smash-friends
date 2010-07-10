################################################################################
# copyright 2010 Lucas Baudin <xapantu@gmail.com>                              #
#                                                                              #
# This file is part of Ultimate Smash Friends.                                 #
#                                                                              #
# Ultimate Smash Friends is free software: you can redistribute it and/or      #
# modify it under the terms of the GNU General Public License as published by  #
# the Free Software Foundation, either version 3 of the License, or (at your   #
# option) any later version.                                                   #
#                                                                              #
# Ultimate Smash Friends is distributed in the hope that it will be useful, but#
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# Ultimate Smash Friends.  If not, see <http://www.gnu.org/licenses/>.         #
################################################################################

import pygame
import os
from os.path import join

from widget import Widget, get_scale, optimize_size
from usf import loaders
from usf.font import fonts
config = loaders.get_config()

from box import HBox


class Paragraph(Widget):

    def __init__(self, path):
        self.defil = 0
        self.state = False
        self.slider_y = 0
        self.hover = False

        self.text = open(join(config.sys_data_dir, 'text', path), 'r').readlines()
        self.text_height = loaders.text("", fonts['mono']['normal']).get_height()
        self.init()

    def update_defil(self):
        self.slider_y = self.defil*(self.height - self.height_slider)/100

    def init(self):
        #the slider (at left)
        self.width_slider = self.width/20
        self.height_slider = self.height/2.5
        self.pos_slider = self.width/20*19
        
        #the main surface
        self.surface = pygame.surface.Surface((self.width, self.height))
        
        #create the surface whiwh will contain _all_ the text
        self.surface_text = pygame.surface.Surface((self.width - self.width_slider*2,
                                                    len(self.text)*self.text_height))
        #draw all the text into the surface
        for i in range(len(self.text)):
            self.text[i] = self.text[i].replace('\n', "")
            self.surface_text.blit(loaders.text(self.text[i],
                                                fonts['mono']['normal']),
                                   (10, self.text_height*i  ))

    def draw(self):
        #clear the surface
        self.surface = self.surface.convert().convert_alpha()
        #draw the text
        self.surface.blit(self.surface_text,
                          (0, -(self.defil*(self.surface_text.get_height()-self.height)/100)))

        #the slider background
        self.surface.blit(loaders.image(join(config.sys_data_dir,
                                             "gui",
                                             config.general['THEME'],
                                             "sliderh_background.png"),
                                        scale=(self.width_slider, self.height))[0],
                          (self.pos_slider, 0))

        #the slider center
        if self.hover:
            slider_center = "sliderh_center_hover.png"
        else:
            slider_center = "sliderh_center.png"

        self.surface.blit(loaders.image(join(config.sys_data_dir,
                                             "gui",
                                             config.general['THEME'],
                                             slider_center),
                                        scale=(self.width_slider, self.height_slider))[0],
                          (self.pos_slider, self.slider_y))

        #foreground
        self.surface.blit(loaders.image(join(config.sys_data_dir,
                                             "gui",
                                             config.general['THEME'],
                                             "paragraph_foreground.png"),
                                        scale=(self.width - self.width_slider*2, self.height))[0],
                          (0, 0))
        return self.surface

    def handle_mouse(self,event):
        x = event.dict['pos'][0]
        y = event.dict['pos'][1]
        if self.state == True:
            #relative position
            x += - self.parentpos[0] - self.x
            y += - self.parentpos[1] - self.y

        if event.type == pygame.MOUSEBUTTONUP:
            self.state = False
            return self,False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            #scroll button (up)
            if event.dict['button'] == 4:
                if 0 <= self.defil - 5 <= 100:
                    self.defil -= 5
            #scroll button (down)
            if event.dict['button'] == 5:
                if 0 <= self.defil + 5 <= 100:
                    self.defil += 5
            self.update_defil()

        #left click or mouse hover
        if((event.type == pygame.MOUSEBUTTONDOWN and event.dict['button'] == 1) or
            event.type == pygame.MOUSEMOTION):
            if (self.pos_slider < event.dict['pos'][0] < self.width and
                self.slider_y < event.dict['pos'][1] < self.slider_y + self.height_slider):
                if event.type == pygame.MOUSEBUTTONDOWN:
                    self.diff_pointer_slider = y - self.slider_y
                    self.state = True
                self.hover = True
                #return False,self
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.state = False
                #self.update_defil()
                return False,False
            elif not self.state:
                self.hover = False

        #if the mouse move the slider
        if self.state and (event.type == pygame.MOUSEMOTION or
                           event.type == pygame.MOUSEBUTTONDOWN):
            y -= self.diff_pointer_slider
            if 0 <= y <= (self.height - self.height_slider):
                self.defil = y * 100 / (self.height - self.height_slider)
            elif y <= 0:
                self.defil = 0
            else:
                self.defil = 100
            self.update_defil();
            return False,self

        return False,False


