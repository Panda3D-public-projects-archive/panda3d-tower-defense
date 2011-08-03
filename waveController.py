from gameAssets import *

from direct.showbase.DirectObject import DirectObject


ENEMY_CODES = { 'p' : Pawn,
                'r' : Rook,
                'b' : Bishop }

class WaveController(DirectObject):
    def __init__(self, file, startBlock, map):
        self.startBlock = startBlock
        self.map = map
        self.loadWaves(file)
        self.enemyRoot = render.attachNewNode('enemy_root')
        self.enemyList = []
        self.livingEnemies = 0
        
        self.accept('enemy_removed', self.handleEnemyRemoved)
        
    # Loads the wave information from the file
    def loadWaves(self, file):
        fileName = 'maps/' + file + '.wave'
        self.waves = []
        
        FILE = open(fileName, 'r')
        while( 1 ):
            line = FILE.readline()
            if( not line ):
                break
            print line,
            if( line[-1] == '\n' ):
                line = line[:-1]
            self.waves.append(line)
            
    def start(self):
        if( len(self.waves) > 0 ):
            self.runWave( self.waves.pop(0) )
                      
    def runWave(self, wave):
        self.enemyList = []
        self.livingEnemies = 0
        self.currentWave = list(wave)
        self.startEnemy()
            
    def startEnemy(self, task = None):
        if( len(self.currentWave) > 0 ):
            enemyCode = self.currentWave.pop(0)
            enemy = self.loadEnemey(enemyCode)
            enemy.setIndex( len(self.enemyList) )
            self.livingEnemies += 1
            self.enemyList.append(enemy)
            enemy.moveToEnd()
            
            taskMgr.doMethodLater(enemy.moveSpeed, self.startEnemy, 'startEnemy')
                            
                            
    def loadEnemey(self, code):
        return ENEMY_CODES[code]( self.enemyRoot, self.startBlock, self.map )
    
    def handleEnemyRemoved(self, enemy):
        self.livingEnemies -= 1
        if( not self.currentWave and self.livingEnemies < 1):
            self.start()
            
    def getEnemy(self, index):
        return self.enemyList[index]