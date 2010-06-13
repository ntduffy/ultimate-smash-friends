################################################################################
# copyright 2010 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
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

from screen import Screen
import widgets
import copy
import pygame
class main_screen(Screen):
    def init(self):
        self.add(widgets.HBox())
        vbox = widgets.VBox()
        self.widget.add(vbox, margin=300)
        vbox.add(widgets.Button('Local game'), margin=150, size=(180,50))
        vbox.add(widgets.Button('Configure'), margin=10, size=(180,50))
        vbox.add(widgets.Button('Credits'), margin=10, size=(180,50))
        vbox.add(widgets.Button('Quit'), margin=10, size=(180,50))
        #vbox.add(widgets.Slider('slider'), margin=10, size=(180,20))
    def callback(self,action):
        if action.text == 'Local game':
            return 'goto:local_game'
        if action.text == 'Configure':
            return 'goto:configure'
        if action.text == 'Credits':
            return 'goto:about'
        if action.text == 'Quit':
            pygame.event.post( pygame.event.Event(pygame.QUIT) )
            
