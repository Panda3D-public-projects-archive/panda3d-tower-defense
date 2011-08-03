from gameAssets import *

from direct.showbase.DirectObject import DirectObject

class TowerController(DirectObject):
    def __init__(self, waveController ):
        self.towers = []
        self.waveController = waveController
        self.enemyRoot = waveController.enemyRoot
        self.currentTowerType = StunTower
        
    # Adds a tower to the block
    def addTower(self, block):
        if( self.currentTowerType ):
            t = block.addTower( self.currentTowerType )
            if( t ):
                self.towers.append(t)
            
    # Called each frame; makes sure every tower
    # is doing what it's supposed to be doing
    def updateTowers(self):
        for tower in self.towers:
            if( tower.targetWithinRange() ):
                tower.attack()
            else:
                tower.notAttacking()
                self.findEnemy(tower)
          
    # Finds an enemy for the tower to attack
    def findEnemy(self, tower):
        tower.cTrav.traverse( self.enemyRoot )
        if( tower.cHandler.getNumEntries() > 0 ):
            enemyIndex = int( tower.cHandler.getEntry(0).getIntoNode().getTag('index') )
            if( not tower.target ):
                tower.model.setColor( Vec4(1, 0, 0, 0.2) )
            tower.target = self.waveController.getEnemy( enemyIndex )
            