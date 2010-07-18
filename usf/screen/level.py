################################################################################
# copyright 2009 Gabriel Pettier <gabriel.pettier@gmail.com>                   #
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

#standard imports
from os.path import join
import os

#our modules
from screen import Screen
from usf import widgets
from usf import loaders
#config
config = loaders.get_config()


class level(Screen):

    def init(self):
        self.add(widgets.VBox())
        basename = join(config.sys_data_dir, "test", "")
        
        coverflow_data = []
        #create a level image for every directory in the level directory.
        files = os.listdir(
                os.path.join(
                    config.sys_data_dir,
                    'levels'
                    )
                )
        files.sort()
        for file in files:
            try:
                if '.xml' in file :
                    coverflow_data.append([])
                    coverflow_data[-1].append(file.replace(".xml",""))
                    coverflow_data[-1].append(join(config.sys_data_dir,
                                                   "gui",
                                                   "image",
                                                   file.replace(".xml","") + ".png"))
            except :
                #logging.debug(file+" is not a valid level.")
                raise
                pass

        self.coverflow = widgets.Coverflow(coverflow_data)
        self.widget.add(self.coverflow, size=(800, 275))
        self.widget.add(widgets.Button(_('Go !')), margin_left=290)
        self.widget.add(widgets.Button(_('Back')), size=(150, 40), margin_left=20, margin=20)
    
    def get_level(self):
        return self.coverflow.get_value()
    
    def callback(self, action):
        if action.text == _('Go !'):
            return "game:new"

        if action.text == _('Back'):
            return "goto:back"