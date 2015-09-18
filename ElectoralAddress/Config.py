'''
Created on 14/09/2015

@author: splanzer
'''

import ConfigParser
Config = ConfigParser.ConfigParser()
Config.read("/home/splanzer/AIMS_config.ini") #where ever the config file may be

def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
        except:
            dict1[option] = None
    return dict1
