#!/usr/bin/env python2

#  Copyright (C) 2011  Edwin Marshall <emarshall85@gmail.com>

#   This file is part of Ultimate Smash Friends.
#
#   Ultimate Smash Friends is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Ultimate Smash Friends is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Ultimate Smash Friends.  If not, see <http://www.gnu.org/licenses/>.

""" Provides a class used for reading and writing various configurable options
    throughout the game

    This class produces an INI formated config file as opposed to an XML
    formatted one. The reason that python's built-in ConfigurationParser isn't 
    sufficient is because comments aren't preserved when writing a config
    file, the order in which the options are written isn't preserved, and the 
    interface used with this class is arguably more convenient that
    ConfigParser's.

    A default config file may be generated by envoking this module from the

    command line:
        python -m config.py [-f filename]

    where filename is an optional name for the config file (system.cfg by default)
"""

from __future__ import with_statement
import os
import sys
import platform

DEFAULT_CONFIG = """\
[keyboard]
PL1_A = K_SEMICOLON
PL1_B = K_m
PL1_C = K_k
PL1_DOWN = K_DOWN
PL1_LEFT = K_LEFT
PL1_RIGHT = K_RIGHT
PL1_SHIELD = K_p
PL1_UP = K_UP
PL2_A = K_c
PL2_B = K_v
PL2_C = K_f
PL2_DOWN = K_s
PL2_LEFT = K_a
PL2_RIGHT = K_d
PL2_SHIELD = K_x
PL2_UP = K_w
PL3_A = K_y
PL3_B = K_t
PL3_C = K_y
PL3_DOWN = K_n
PL3_LEFT = K_h
PL3_RIGHT = K_j
PL3_SHIELD = K_b
PL3_UP = K_u
PL4_A = K_KP2
PL4_B = K_KP1
PL4_C = K_t
PL4_DOWN = K_KP5
PL4_LEFT = K_KP4
PL4_RIGHT = K_KP6
PL4_SHIELD = K_KP9
PL4_UP = K_KP8
QUIT = K_ESCAPE
TOGGLE_FULLSCREEN = K_F11
VALIDATE = K_RETURN

[audio]
SOUND = True
SOUND_VOLUME = 100
MUSIC = True
MUSIC_VOLUME = 100

[general]
DEBUG = True
SHOW_FPS = False
NETWORK_PORT = 8421
FULLSCREEN = False
NOTIF_EFFECT = True
WIDTH = 0
MAX_FPS = 30
MAX_GUI_FPS = 30
LOG_FILENAME = usf.log
GRAVITY = 1962
INVINCIBLE_TIME = 3000
HEIGHT = 0
WALKSPEED = 200
AIR_FRICTION = 3
THEME = tty
CONFIRM_EXIT = True
ZOOM_SHARPNESS = 50
SMOOTHSCALE = True
JUMPHEIGHT = 48.0
SHIELD_SOLIDITY = 6000.0
POWER_SHIELD_TIME = 0.2
SMOOTH_SCROLLING = True
BOUNCE = .2

[debug]
CONTROLS = False
ACTIONS = False
HARDSHAPES = False
FOOTRECT = False
CURRENT_ANIMATION = False
LEVELSHAPES = False
LOG_FILENAME = usf.log
LOG_LEVEL = WARN
LEVELMAP = False
"""


#TODO: add logging to replace print statements
class Section(object):
    """ An object that represents a section in a config file.

        Options can be added to a section by simply assigning a value to an 
        attribute: section.foo = baz
        would produce:
            [section]
            foo = baz
        in the config file. Options that do not exist on assignment
        are created dynamcially.

        Values are automatically converted to the appropriate python type. 
        Options that begin and end with brackets([, ]) are converted to lists,
        and options that are double-quoted (") are converted to strings. 
        Section also recognizes booleans regardless of case, in addition to the
        literals 'yes' and 'no' of any case. Except in the case of 
        double-quoted strings, extra white-space is trimmed, so you need not 
        worry. For example:
            foo = bar
        is equivalent to :
            foo    =         baz
    """
    def __init__(self, name):
        """ Initialize a new section.

            @param name: name of the section. In the INI file, sections are surrounded
                         by brackets ([name])
            @type name: string
        """
        self.name = name

    def __setattr__(self, option, value):
        """ Assign a value to an option, converting types when appropriate.

            @param option: name of the option to assign a value to.
            @type option: string @param value: value to be assigned to the option.
            @type value: int, float, string, boolean, or list
        """
        value = str(value)
        if value.startswith('[') and value.endswith(']'):
            value = [item.strip() for item in value[1:-1].split(',')]
        elif value.lower() == 'true' or value.lower() == 'yes':
            value = True
        elif value.lower() == 'false' or value.lower() == 'no':
            value = False
        elif value.isdigit():
            value = int(value)
        else:
            try:
                value = float(value)
            except ValueError:
                # leave as string
                pass

        self.__dict__[option] = value

    def __getattribute__(self, option):
        """ Returns the option's value"""

        # Remove leading and trailing quotes from strings that have them
        return_value = object.__getattribute__(self, option)
        try:
            for key, value in return_value.iteritems():
                if (hasattr(value, 'split') and 
                    value.startswith("\"") and value.endswith("\"")):
                    return_value[key] = value[1:-1]
        except AttributeError:
            pass

        return return_value

    @property
    def entries(self):
        """ Returns a dictionary of existing entries """
        entries = self.__dict__
        # get rid of properties that aren't actually options
        if entries.has_key('name'):
            entries.pop('name')

        return entries

    @property
    def options(self):
        """ Returns a list of existing options """
        entries = self.entries
        return entries.keys()

    @property
    def values(self):
        """ Returns a list of existing values """
        entries = self.entries
        print entries.values()
        return entries.values()


class Config(object):
    """ An object that represents a config file, its sectons,
        and the options defined within those sections.
    """
    def __init__(self, config_path='', system_path='', user_path='',
                 filename='user.cfg'):
        """ initializes a new config object. If no paths are given, they are
            guessed based on whatever platform the script was run on.

            Examples:
                paths = ['/etc/ultimate-smash-friends', 
                         '/home/user_name/.config/ultimate-smash-friends']
                config = Config(*paths)
                
                paths = {'system': '/etc/ultimate-smash-friends', 
                         'user': '/home/user_name/.config/ultimate-smash-friends'}
                config = Config(**paths)

                config = Config('.')

                config = Config()

            @param system_path: Path to the system config file.
            @type system_path: string (must be a valid path)

            @param user_path: Path to the user config file. Options that
                              are missing from this file are propogated 
                              from the system config file and saved on
                              request
            @type user_path: string (must be a valid path)
            
            @param filename: Filename of the user config file that will be 
                             generated.
            @type filename: string
        """
        self._filename = filename
        self._config_file = []
        self._paths = {}

        if not system_path and not user_path and not config_path:
            # use platform-specific values as paths
            (self._paths['system'], 
             self._paths['user'], 
             self._paths['config']) = self.platform_paths()
        else:
            # convert supplied paths to absolute paths
            abs_paths = [os.path.expanduser(path)
                         for path in [system_path, user_path, config_path]]
            (self._paths['system'], self._paths['user'],
             self._paths['config']) = abs_paths

        self.read()

    def __getattr__(self, name):
        """ Returns a Section object to be used for assignment, creating one
            if it doesn't exist.

            @param name: name of section to be retrieved
            @type name: string
        """
        if not self.__dict__.has_key(name) and not name.startswith('_'):
            setattr(self, name, Section(name))

        return object.__getattribute__(self, name)

    @staticmethod
    def platform_paths(system=None):
        if system is None:
            system = os.name
        
        if system in ['posix', 'linux']:
            return (os.path.join(os.sep, 'usr', 'share', 'ultimate-smash-friends'),
                    os.path.join(os.environ['XDG_CONFIG_HOME'], 'ultimate-smash-friends'),
                    os.path.join(os.sep, 'etc', 'ultimate-smash-friends'))
        elif system in ['nt', 'windows', 'vista']:
            return (os.path.join(os.environ['PROGRAMFILES'], 'Ultimate Smash Friends'),
                    os.path.join(os.environ['USERDATA'], 'Ultimate Smash Friends'),
                    os.path.join(os.environ['PROGRAMFILES'], 'Ultimate Smash Friends'))
        elif system in ['mac']:
            return (os.path.join(os.sep, 'Library', 'Application Support', 
                                 'Ultimate Smash Friends'),
                    os.path.join(os.environ['HOME'], 'Library', 
                                 'Application Support', 
                                 'Ultimate Smash Friends'),
                    os.path.join(os.sep, 'Library', 'Preferences', 
                                 'Ultimate Smash Friends'))
        else:
            return None

    @staticmethod
    def generate(filename):
        """ Takes filename and generates a default config file using 
            DEFAULT_CONFIG
        """

        with open(filename, 'w') as f:
            for line in DEFAULT_CONFIG:
                f.write(line)

    def update(self, filename=None):
        """ This method simply removes invalid options from the config
            file. If the file is not writable, a useful error message is 
            thrown.
        """

        #TODO: error detection (try/except)

        if filename is None:
            filename = os.path.join(self.user_path, self._filename)

        default_options = []
        new_options = []
        lines = []

        for line in DEFAULT_CONFIG.split('\n'):
            if not line.startswith('[') and len(line) != 0:
                default_options.append(line.split(' ')[0])

        with open(filename, 'r') as infile:
            for line in infile.readlines():
                lines.append(line)
                if not line.startswith('[') and len(line) != 0:
                    new_options.append(line.split(' ')[0])

        # find items that are in new_options but not in default_options
        differences = set(new_options).difference(set(default_options))

        # ignore line breaks
        differences = [option for option in list(differences) if option != '\n']

        with open(filename, 'w') as outfile:
            for line in lines:
                for option in differences:
                    if option not in line:
                        outfile.write(line)

    def read(self, filenames=None):
        """ Reads a config file and populates the config object 
            with its sections and options. Calling this method without
            any arguments simply re-reads the previously defined filename
            and paths

            @param filenames: name of files to be parsed. 
            @type path: string or list
        """

        if filenames is None:
            filenames = [os.path.join(self._paths['config'], 'system.cfg'),
                         os.path.join(self._paths['user'], self._filename)]

        elif hasattr(filenames, 'split'):
            filenames = [filenames]

        for filename in filenames:
            section = None
            if os.path.exists(filename):
                try:
                    self._config_file = open(filename, 'r').readlines()
                except IOError as (errno, strerror):
                    if errno == 2:
                        if os.path.basename(filename).startswith('system'):
                            print ('{0} could not be found. Please supply a '
                                   'different path or generate a system config '
                                   'file with:\n'
                                   'python2 -m usf.config').format(filename)
                            sys.exit(1)
                    else:
                        print 'Error No. {0}: {1} {2}'.format(errno, filename, strerror)
                        sys.exit(1)

                for line in self._config_file:
                    if line.startswith('#') or line.strip() == '':
                        continue
                    elif line.startswith('[') and line.endswith(']\n'):
                        getattr(self, line[1:-2])
                        section = line[1:-2]
                    else:
                        option, value = [item.strip() 
                                         for item in line.split('=', 1)]
                        setattr(getattr(self, section), option, value)

        self._config_read = True

    def write(self, filename=None):
        """ Writes a config file based on the config object's 
            sections and options

            @param filename: Name of file to save to. By default, this is
                             the user config file.
            @type path: string
        """
        if filename is None:
            filename = os.path.join(self.user_path, 'user.cfg')

        for section in self.sections:
            section_tag = "[{0}]\n".format(section)
            # add new sections to config file
            if section_tag not in self._config_file:
                self._config_file.append(section_tag)

                for option, value in getattr(self, 
                                             section).entries.iteritems():
                    self._config_file.append("{0} = {1}").format(option, value)
            else:
                # find new options and place them in the appropriate section
                end_of_section = self._config_file.index(section_tag) + 1
                for option, value in (getattr(self, 
                                      section).entries.iteritems()):
                    end_of_section += 1
                    template = "{0} = {1}\n".format(option, str(value))
                    
                    for index, line in enumerate(self._config_file[:]):
                        if line.startswith(option):
                            isNewOption = False
                            self._config_file[index] = template
                            break
                        else:
                            isNewOption = True

                    if isNewOption:
                        self._config_file[end_of_section] = template

        # write file
        with open(filename, 'w') as outfile:
            for line in self._config_file:
                outfile.write(line)

    @property
    def sections(self):
        """ Returns a list of existing sections"""
        return [key for key in self.__dict__.keys() if not key.startswith('_')]
        sections = self.__dict__.keys()

        return sections

    @property
    def paths(self):
        return self._paths

    @property
    def system_path(self):
        return self._paths['system']

    @property
    def user_path(self):
        return self._paths['user']

    @property
    def config_path(self):
        return self._paths['config']


if __name__ == '__main__':
    from optparse import OptionParser

    usage = "usage: %prog [options] system[, system, ...]"
    parser = OptionParser(usage=usage)

    parser.add_option('-f', '--filename', default='system.cfg',
                      help='Filename of output configuration file')

    opts, args = parser.parse_args()
    
    Config.generate(opts.filename)
