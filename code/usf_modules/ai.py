################################################################################
# copyright 2008 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by the Free#
# Software Foundation, either version 3 of the License, or (at your option) any#
# later version.                                                               #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful, but  #
# WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or#
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for    #
# more details.                                                                #
#                                                                              #
# You should have received a copy of the GNU General Public License along with #
# UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.           #
################################################################################
import time

from usf_modules.new_config import Config
config = Config()
general = config.general
sound_config = config.audio
SHARE_DIRECTORY = config.config_dir
MEDIA_DIRECTORY = config.data_dir
SIZE = (general['WIDTH'], 
        general['HEIGHT'])
import pygame
class AI(object):
    sequences_ai = []
    def update_enemy (self) :
        """
        This function update the information about different enemys
        """

        self.enemy_number = []
        self.enemy_position = []
        self.enemy_distance = []
        self.enemy_distanceh = []

        for pl in [pl for pl in self.game.players if pl is not self.iam] :
            self.enemy_number.append (pl.num)
            self.enemy_position.append (pl.place)
            self.enemy_distance.append (self.iam.dist (pl))
            self.enemy_distanceh.append (pl.place[1]- self.iam.place[1])
    def update(self, game, iam):
        self.sequences_ai = []
        self.num = iam
        self.iam = game.players[iam]
        self.game = game
        self.update_enemy()
        self.choose_strategy()
    def choose_strategy(self):
        """if(self.iam.place[0] <self.enemy_position[0][0]):
            self.sequences_ai.append(("PL"+ str(self.num) + "_RIGHT",time.time()))
            self.iam.walking_vector[0] = config['WALKSPEED']
            self.iam.reversed = False
        if(self.iam.place[0] >self.enemy_position[0][0]):
            self.sequences_ai.append(("PL"+ str(self.num) + "_LEFT",time.time()))
            self.iam.walking_vector[0] = config['WALKSPEED']
            self.iam.reversed = True"""
        aix = self.iam.place[0]/8
        aiy = self.iam.place[1]/8
        enx = self.enemy_position[0][0]/8
        eny = self.enemy_position[0][1]/8
        pygame.draw.line(self.game.screen, pygame.Color("red"), (aix,aiy), (enx,eny))
        pygame.display.update()
        self.iam.walking_vector[0] = 0
        if self.enemy_position[0][0] < self.iam.place[0] :
            self.iam.reversed = True
        else :
            self.iam.reversed = False
        if self.enemy_distanceh[0] < 20 and self.enemy_distanceh[0] > -20:
            self.iam.walking_vector[0] = general['WALKSPEED']
            self.sequences_ai.append(("PL"+ str(self.num+1) + "_LEFT",time.time()))
        if self.enemy_distance[0] < 100 :
            self.sequences_ai.append(("PL"+ str(self.num+1) + "_B",time.time()))
