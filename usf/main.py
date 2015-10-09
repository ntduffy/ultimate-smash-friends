#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
# copyright 2008-2011 Gabriel Pettier <gabriel.pettier@gmail.com>              #
#                                                                              #
# This file is part of UltimateSmashFriends                                    #
#                                                                              #
# UltimateSmashFriends is free software: you can redistribute it and/or modify #
# it under the terms of the GNU General Public License as published by         #
# the Free Software Foundation, either version 3 of the License, or            #
# (at your option) any later version.                                          #
#                                                                              #
# UltimateSmashFriends is distributed in the hope that it will be useful,      #
# but WITHOUT ANY WARRANTY; without even the implied warranty of               #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the                #
# GNU General Public License for more details.                                 #
#                                                                              #
# You should have received a copy of the GNU General Public License            #
# along with UltimateSmashFriends.  If not, see <http://www.gnu.org/licenses/>.#
################################################################################

'''
This is the main file for ultimate-smash-friends, that initiate configs, parse
parameters, and initiate games

'''

import logging
import os
import sys

from pygame.locals import QUIT
import pygame
from argparse import ArgumentParser
import threading

from usf.game import Game, NetworkServerGame #, NetworkClientGame
from usf.gui import Gui
from usf.controls import Controls

from usf.music import Music
from usf.font import fonts
from usf.ai import AI

from usf.translation import _


from usf import loaders
from usf import CONFIG

logging.basicConfig(
    filename=os.path.join(CONFIG.user_path, CONFIG.debug.LOG_FILENAME),
    level=(CONFIG.debug.LOG_LEVEL)
)

logging.debug("""Paths:
        Config:
        System: {0}
        User: {1}

        Filename: {2}""".format(*CONFIG.paths.keys() + [CONFIG.filename]))

def author():
    """ print credits in the terminal
    """
    if 'CREDITS' not in os.listdir(os.path.join(CONFIG.system_path)):
        logging.info(CONFIG.system_path)
        logging.info('\n'.join(os.listdir(os.path.join(CONFIG.system_path))))
        logging.debug(CONFIG.system_path +'/CREDITS file not found')

    else:
        author_file = open(os.path.join(CONFIG.system_path, 'CREDITS'))
        logging.info(author_file.read())
        author_file.close()


class Main(object):
    """
    The main class, load some parameters, sets initial states and takes care of
    the game main loop.
    """

    def __init__(self, players=None, level=None):
        """
        The constructor, create the render surface, set the menu initial state,
        parse command line params if any, launch the menu or the game depending
        on parameters.

        The init parameter determines if the Main object should be initialized
        once instanciated. The run parameter determines if the game should be run
        once the object is instantiated and initiated.

        """
        self.lock = threading.Lock()
        self.stop_thread = False
        self.text_thread = _("Loading...")

        self.level = level
        if players is None:
            self.players = []

        self.init()
        self.run()

    def init(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.controls = Controls()
        self.initialized = False

        try:
            self.init_standalone()
            self.initialized = True
        except:
            self.stop_thread = True
            self.initialized = False
            raise

    def init_standalone(self):
        '''
        start a non network instance of the game
        '''

        self.init_screen()
        self.text_thread = "Loading sounds and musics..."
        thread = threading.Thread(None, self.loading_screen)
        thread.start()

        self.init_sound()
        self.ai_instance = AI()

        # if a level was provided and at least two players in the option
        # immediatly jump into game mode
        if len(self.players) > 1 and self.level is not None:
            self.game = Game(self.screen, self.level, self.players)
            self.state = "game"
            self.menu = Gui(self.screen)
            self.menu.handle_reply({'goto': 'configure'})
        else:
            self.lock.acquire()
            self.text_thread = "Loading GUI..."
            self.lock.release()

            self.menu = Gui(self.screen)

            self.state = "menu"

            self.game = None
            self.level = None

        self.lock.acquire()
        self.stop_thread = True
        self.lock.release()
        thread.join()
        # end of loading resources



    def init_screen(self):
        """ various screen initialisations
        """
        size = (CONFIG.general.WIDTH, CONFIG.general.HEIGHT)
        if (CONFIG.general.WIDTH, CONFIG.general.HEIGHT) == (0, 0):
            if (800, 600) in pygame.display.list_modes():
                (CONFIG.general.WIDTH, CONFIG.general.HEIGHT) = (800, 600)

            else:
                #the old default value...
                (CONFIG.general.WIDTH, CONFIG.general.HEIGHT) = (800, 480)
            CONFIG.display.FULLSCREEN = False

        size = (CONFIG.general.WIDTH, CONFIG.general.HEIGHT)
        self.screen = pygame.display.set_mode(size)

        pygame.display.set_caption('Ultimate Smash Friends')
        icon = loaders.image(os.path.join(CONFIG.system_path, 'icon',
                                          'icon_50.png'))[0]
        pygame.display.set_icon(icon)
        if CONFIG.display.FULLSCREEN:
            pygame.display.toggle_fullscreen()

    def init_sound(self):
        """ various audio initialisations
        """
        self.music = Music()

    def manage_menu(self):
        """ manage input and update menu if we are in the menu state
        """
        # return of the menu update function may contain a new game
        # instance to switch to.
        start_loop = pygame.time.get_ticks()
        menu_was = self.menu.current_screen
        newgame, game_ = self.menu.update()
        if menu_was == 'keyboard' and self.menu.current_screen != 'keyboard':
            self.controls.load_keys()
            self.controls.load_sequences()

        if newgame:
            self.state = 'game'
            if game_ is not self.game:
                print "starting game"
                self.ai_instance = AI()

                del(self.game)
                self.game = game_

        max_fps = 1000/CONFIG.general.MAX_GUI_FPS

        if self.menu.current_screen == 'about':
            self.music_state = 'credits'
        else:
            self.music_state = self.state

        if pygame.time.get_ticks() < max_fps + start_loop:
            pygame.time.wait(max_fps + start_loop - pygame.time.get_ticks())

    def manage_ai(self):
        """ update the ai
        """
        for i, p in enumerate(self.game.players):
            if p.ai and p.present:
                self.ai_instance.update(self.game, i)

    def manage_game(self, dt):
        """ call the various submethod to update the whole game and render it
	    to the screen
        """
        #d = self.game.update_clock(was_paused or self.game.first_frame)
        self.state = self.game.update(dt)
        self.manage_ai()

        if self.state in ('game', 'victory'):
            self.game.draw(
                debug_params={
                    'controls': CONFIG.debug.CONTROLS and self.controls,
                    'action': CONFIG.debug.ACTIONS,
                    'hardshape': CONFIG.debug.HARDSHAPES,
                    'footrect': CONFIG.debug.FOOTRECT,
                    'current_animation': CONFIG.debug.CURRENT_ANIMATION,
                    'levelshape': CONFIG.debug.LEVELSHAPES,
                    'levelmap': CONFIG.debug.LEVELMAP})

            self.menu.load = False
        else:
            self.menu.current_screen = "main_screen"

        self.music_state = self.state

    def display_fps(self):
        """ FPS counter
        """
        if CONFIG.display.SHOW_FPS:
            self.screen.blit(
                    loaders.text(
                        "FPS: " + str(self.clock.get_fps()),
                        fonts["mono"]["38"]),
                    (10, 5))

    def run(self):
        """
        The main game loop, take care of the state of the game/menu.
        """

        if not self.initialized:
            return False

        pygame.mouse.set_visible(False)
        self.clock.tick()

        while (True):
            # poll controls and update informations on current state of the UI
            state_was = self.state

            if self.game:
                dt = self.clock.tick(CONFIG.general.MAX_FPS) / 1000.0
            else:
                dt = self.clock.tick(CONFIG.general.MAX_GUI_FPS) / 1000.0

            if self.state != "menu":
                self.state = self.controls.poll( self.game, self.menu)

            # this depends on the previous assertion, it's NOT an elif
            if self.state == "menu":
                self.manage_menu()

            else:
                # update the fps counter
                if state_was == "menu":
                    dt = 0

                self.manage_game(dt)

            self.display_fps()
            pygame.display.update()

            if CONFIG.audio.MUSIC:
                self.music.update(self.music_state)

            # verify there is not a QUIT event waiting for us, in case of we
            # have to quit.
            self.ended = pygame.event.get(QUIT)
            if self.ended:
                logging.debug('fps = '+str(self.clock.get_fps()))
                pygame.quit()
                break

    def loading_screen(self):
        """
        update the screen display during loading
        """
        while not self.stop_thread:
            self.lock.acquire()
            text = loaders.paragraph(self.text_thread, fonts['mono']['normal'])
            self.lock.release()

            x = self.screen.get_width()/2 - text.get_width()/2
            y = self.screen.get_height()/2 - text.get_height()/2

            self.screen.fill(pygame.color.Color("black"))
            self.screen.blit(text, (x, y))
            pygame.display.update()

            pygame.time.wait(10)

if __name__ == '__main__':
    # Entry point of the game, if not imported from another script, launch the
    # main class with parameters (appart from program self name) if any.


    parser = ArgumentParser(description="a Smash Bros-like game")
    # Set options and usage to parse users choices

    parser.add_argument(
        '-a', '--authors',
        action='store_true', dest='author',
        help='See authors of this game.'
    )
    parser.add_argument(
        '-v', '--version',
        action='version', version='%(prog)s 0.1.3'
    )
    parser.add_argument(
        '-l', '--level',
        action='store', dest='level', metavar='levelname',
        help='select level by name'
    )
    parser.add_argument(
        '-p', '--players',
        action='store', dest='players', nargs=1, metavar='player1, player2..',
        help='select up to 4 players by name'
    )

    args = vars(parser.parse_args())

    if args.get('author'):
        author()
        sys.exit(1)
    else:
        del args['author']

    if args.get('player'):
        args['players'] = map(
            lambda p: 'characters' + os.sep + p,
            args['players'].split(',')
        )

    # MAIN STARTS HERE
    m = Main(**args)
