import settings
from camera import RTS_Camera
from gameAssets import *
from waveController import WaveController
from towerController import TowerController

from direct.showbase.DirectObject import DirectObject
from panda3d.core import BitMask32, CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionRay
from panda3d.core import Vec4, Vec3
from panda3d.core import AmbientLight,DirectionalLight,LightAttrib

BLOCK_GROUND = '-'
BLOCK_START = 's'
BLOCK_END = 'e'
BLOCK_PATH = 'o'
BLOCK_OTHER = 'x'
BLOCK_CHAR_TO_MODEL = { BLOCK_GROUND : GroundBlock,
                        BLOCK_START : StartBlock,
                        BLOCK_END : EndBlock,
                        BLOCK_PATH : PathBlock,
                        BLOCK_OTHER : OtherBlock }
                        

class GameEngine( DirectObject ):
    def __init__(self):
        print 'Game Engine Started'
        self.lastBlock = 0
        self.map = []
        self.startBlock = 0
        self.endBlock = 0
        self.mapName = 'test2'
        
        self.loadEnvironment(self.mapName)
        self.loadCursorPicker()
        self.camera = RTS_Camera()
        self.loadSimpleLighting()
        
        self.waveController = WaveController(self.mapName, self.startBlock, self.map)
        self.towerController = TowerController(self.waveController)
        
        self.setupKeyListeners()
        self.EFT = taskMgr.add(self.everyFrameTask, "everyFrameTask")
        
    # The task that is run every frame
    def everyFrameTask(self, task):
        self.camera.handleMouseInput()
        self.checkCursorCollision()
        self.towerController.updateTowers()
        
        return task.cont
    
    # Loads the level from the text file. Puts each
    # row into an array then creates the rows in the
    # 1st quadrant
    def loadEnvironment(self, file):
        fileName = 'maps/' + file + '.map'
        rows = []
        self.environmentRoot = render.attachNewNode('environmentRoot')
        
        FILE = open(fileName, 'r')
        while( 1 ):
            line = FILE.readline()
            if( not line ):
                break
            print line,
            if( line[-1] == '\n' ):
                line = line[:-1]
            rows.append(line)
            
        rows.reverse()
        for i, row in enumerate(rows):
            self.createRow( i, row )
            
    # Loads the models corresponding to the
    # characters in the map file for an entire row
    def createRow(self, rowIndex, row):
        mapRow = []
        
        for colIndex, block in enumerate(row):
            block = BLOCK_CHAR_TO_MODEL[block]( self.environmentRoot, colIndex + 0.5, rowIndex + 0.5 )
            mapRow.append( block )
            block.setIndex( str(rowIndex) + ' ' + str(colIndex) )
            
            if( block.isType(StartBlock) ):
                self.startBlock = block
            elif( block.isType(EndBlock) ):
                self.endBlock = block
                
        self.map.append(mapRow)
            
    # Creates necessary collision parts to determine what object
    # the cursor is hovering
    def loadCursorPicker(self):
        self.picker = CollisionTraverser()
        self.pq     = CollisionHandlerQueue()
        self.pickerNode = CollisionNode('mouseRay')
        self.pickerNP = camera.attachNewNode(self.pickerNode)
        self.pickerNode.setFromCollideMask(BitMask32.bit(1))
        self.pickerRay = CollisionRay()
        self.pickerNode.addSolid(self.pickerRay)
        self.picker.addCollider(self.pickerNP, self.pq)
        
    def checkCursorCollision(self):
        if base.mouseWatcherNode.hasMouse():
              mpos = base.mouseWatcherNode.getMouse()
              self.pickerRay.setFromLens( base.camNode, mpos.getX(), mpos.getY() )
              
        self.picker.traverse( self.environmentRoot )
        if( self.pq.getNumEntries() > 0 ):
            self.pq.sortEntries()
            (row, ignore, col) = self.pq.getEntry(0).getIntoNode().getTag('index').partition(' ')
            row = int(row)
            col = int(col)
            block = self.map[row][col]
            if( block != self.lastBlock ):
                block.highlight()
                if( self.lastBlock ):
                    self.lastBlock.unHighlight()
            self.lastBlock = block
        else:
            if( self.lastBlock ):
                self.lastBlock.unHighlight()
                self.lastBlock = 0
            
    def mouseClick(self):
        if( self.lastBlock ):
            self.towerController.addTower(self.lastBlock)
            
    def spawnEnemy(self):
        e = Enemy(self.startBlock, self.map)
        e.moveToEnd()
        
    def setTowerType(self, type):
        self.towerController.currentTowerType = type
    
    def setupKeyListeners(self):
        self.accept('mouse1', self.mouseClick)
        self.accept('q', self.waveController.start)
        
        self.accept('1', self.setTowerType, [NormalTower])
        self.accept('2', self.setTowerType, [SlowTower])
        self.accept('3', self.setTowerType, [StunTower])
            
    def loadSimpleLighting(self):
        ambientLight = AmbientLight( "ambientLight" )
        ambientLight.setColor( Vec4(.8, .8, .8, 1) )
        directionalLight = DirectionalLight( "directionalLight" )
        directionalLight.setDirection( Vec3( 0, 45, -45 ) )
        directionalLight.setColor( Vec4( 0.2, 0.2, 0.2, 0.6 ) )
        render.setLight(render.attachNewNode( directionalLight ) )
        render.setLight(render.attachNewNode( ambientLight ) )