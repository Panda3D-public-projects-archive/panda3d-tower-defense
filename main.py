import settings

from gameEngine import GameEngine
from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties, Vec4


class MyApp( ShowBase ):
    def __init__(self):
        ShowBase.__init__(self)
        
        self.game = None

        self.loadConfigurations()
        ## settings.FULLSCREEN = 0
        ## settings.HEIGHT = 600
        ## settings.WIDTH = 800
        self.setupWindow()        
        
        self.start()
        
    def start(self):
        if( not self.game ):
            self.game = GameEngine()
        
    # Alters the state of the window based on the
    # specified configurations in the game settings
    def setupWindow(self):
        wp = WindowProperties()
        wp.setFullscreen(settings.FULLSCREEN)
        wp.setSize(settings.WIDTH, settings.HEIGHT)
        wp.setTitle("GAME")
        base.win.requestProperties(wp)
        base.win.setClearColor(Vec4(0.5, 0.5, 0.8, 1))
    
    # Loads the configurations from the game settings file
    def loadConfigurations(self):
        confFile = {}
        fileName = 'game_settings.ini'
        FILE = open(fileName, 'r')
        while( 1 ):
            line = FILE.readline()
            if(not line):
                break
            print line,
            (var, ignore, data) = line.partition("=")
            confFile[var] = data.strip()
        print '\n'
        
        #settings.NAME = confFile["name"]

        resolution = confFile["resolution"]
        (w, ignore, h) = resolution.partition("x")
        settings.WIDTH = int(w)
        settings.HEIGHT = int(h)
        
        settings.FULLSCREEN = (confFile["fullscreen"] == 'on')
        
        #settings.AUTO_RELOAD = (confFile["auto_reload"] == 'on')

        #settings.MOUSE_SENSITIVITY = float(confFile["mouse_sensitivity"])

        #settings.SERVER = confFile["server"]
        
cz = MyApp()
cz.run()