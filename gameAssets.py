from panda3d.core import Vec3, Vec4, BitMask32
from direct.showbase.DirectObject import DirectObject
from panda3d.core import BitMask32, CollisionTraverser, CollisionNode, CollisionHandlerQueue, CollisionSphere
from direct.gui.DirectGui import DirectWaitBar

VALID_HIGHLIGHT_COLOR = Vec4(36.0/255, 225.0/255, 213.0/255, 1)
INVALID_HIGHLIGHT_COLOR = Vec4(1, 0, 0, 1)

RIGHT = 0
DOWN = 1
LEFT = 2
UP = 3
DIRECTION_TO_VECTOR = { RIGHT : Vec3( 1,  0, 0),
                        DOWN  : Vec3( 0, -1, 0),
                        LEFT  : Vec3(-1,  0, 0),
                        UP    : Vec3( 0,  1, 0) }

SLOW_COLOR = Vec4(0, 0, 1, 0.2)
STUN_COLOR = Vec4(0, 0.5, 0.5, 0.2)

# Parent Class for environment blocks
class Block(DirectObject):
    def __init__(self, model, parent, x, y, z=0.5):
        self.index = -1
        self.tower = 0      # Whether a tower is on top of this block
        
        # Load and position 3D Model
        self.model = loader.loadModel( 'models/' + model )
        self.model.reparentTo( parent )
        self.model.setPos( x, y, z )
        
        # Collision for selecting it with the mouse
        self.geomBlock = self.model.find("**/Cube").node()
        self.geomBlock.setIntoCollideMask( BitMask32.bit(1) )
        
    def setIndex(self, index):
        self.geomBlock.setTag('index', str(index) )
        self.index = index
        
    def highlight(self):
        pass
        
    def unHighlight(self):
        pass
        
    def addTower(self, towerType):
        pass
    
    def getPos(self):
        return self.model.getPos()
    
    # Returns whether the type of this block matches @blockType
    def isType(self, blockType):
        return self.__class__.__name__ == blockType.__name__
            
# A block that can support towers on top of it
class GroundBlock(Block):
    def __init__(self, parent, x, y):
        Block.__init__(self, 'ground', parent, x, y, 1 )
        
    # Highlights the block with different colors depending
    # upon the state of the block
    def highlight(self):
        if( self.tower ):
            self.model.setColor( INVALID_HIGHLIGHT_COLOR )
        else:
            self.model.setColorScale( VALID_HIGHLIGHT_COLOR )
            
    # Removes the highlight
    def unHighlight(self):
        self.model.clearColorScale()
        self.model.clearColor()
        
    # Places a tower on the block
    def addTower(self, towerType):
        t = 0
        if( not self.tower ):
            t = towerType( self.model.getPos() )
            self.tower = t
        return t
            

# A block that indicates where enemies should spawn
class StartBlock(Block):
    def __init__(self, parent, x, y):
        Block.__init__(self,'start', parent, x, y )
      
# A block that indicates the end of the path
class EndBlock(Block):
    def __init__(self,  parent, x, y):
        Block.__init__(self, 'end', parent, x, y )
      
# A block that indicates the path for the enemies to travel on
class PathBlock(Block):
    def __init__(self, parent, x, y):
        Block.__init__(self, 'path', parent, x, y )

# A block that cannot support enemies or towers
class OtherBlock(Block):
    def __init__(self, parent, x, y):
        Block.__init__(self, 'other', parent, x, y )

# The parent class for structures that attack enemies
class Tower(DirectObject):
    def __init__(self, pos):
        self.range = 2          # How many units can the projectile travel
        self.target = 0         # The enemy this tower is attacking
        self.isAttacking = 0    # Whether this tower is attacking
        #self.attackTime = 0.5                           # The number of seconds that must pass between attacks
        self.timeSinceLastAttack = self.attackTime      # The amount of time that has passed since the last attack
        self.damage = 1
        
        # Load and place the model
        self.model = loader.loadModel( 'models/' + self.modelType )
        self.model.reparentTo(render)
        self.model.setPos( pos )
        
        # Listen for the removal of enemies
        self.accept( 'enemy_removed', self.checkIfKilledTarget )
        
        # Setup the collision necessary for finding enemies
        self.setupCollision()
        
    # Checks whether the enemy that was removed is the
    # enemy this tower was attacking
    def checkIfKilledTarget(self, enemy):
        if( self.target == enemy ):
            self.target = 0
            
    # Checks to see if the target it is attacking is still
    # within range
    def targetWithinRange(self):
        if( self.target ):
            return self.model.getDistance(self.target.model) < self.range
        else:
            return 0
        
    # Attack the target
    def attack(self, specialFunctions = None):
        self.timeSinceLastAttack += globalClock.getDt()
        if( self.timeSinceLastAttack > self.attackTime ):
            self.target.takeDamage(self.damage)
            self.timeSinceLastAttack = 0
            
            # If the tower does something special in addition 
            # to attacking, do it
            if( specialFunctions and self.target ):
                for ability in specialFunctions:
                    ability()
                
    def notAttacking(self):
        self.model.clearColor()
        self.target = 0
        self.timeSinceLastAttack += globalClock.getDt()
        
    # Sets up the necessary collision geometry and variables
    # for finding enemies
    def setupCollision(self):
        self.sphere = self.model.attachNewNode( CollisionNode('range') )
        self.sphere.node().addSolid( CollisionSphere(0, 0, 0, self.range) )
        self.sphere.node().setFromCollideMask( BitMask32(2) )
        self.sphere.node().setIntoCollideMask(BitMask32.allOff())
        
        self.cTrav = CollisionTraverser()
        self.cHandler = CollisionHandlerQueue()
        self.cTrav.addCollider(self.sphere, self.cHandler)
        
# A tower with no abilities
class NormalTower(Tower):
    def __init__(self, pos):
        self.attackTime = 0.5       # Time between attack
        self.modelType = 'pawn'
        Tower.__init__(self, pos)
        self.damage = 0.5           # Amount of damage dealt
        
    def attack(self):
        Tower.attack(self, [] )      

# A tower that reduces the speed of the enemy it attacks
class SlowTower(Tower):
    def __init__(self, pos):
        self.attackTime = 1.5       # Time between attack
        self.modelType = 'rook'
        Tower.__init__(self, pos)
        self.slow = 0.5             # What fraction is the speed of the enemy reduced to
        self.slowDuration = 1       # How long does the slow last
        self.damage = 2           # Amount of damage dealt
        
    def attack(self):
        Tower.attack(self, [self.applySlow] )
        
    def applySlow(self):
        self.target.slow( self.slow, self.slowDuration )
        
# A tower that stops the enemy it attacks
class StunTower(Tower):
    def __init__(self, pos):
        self.attackTime = 2       # Time between attack
        self.modelType = 'king'
        Tower.__init__(self, pos)
        self.stunDuration = 1     # How long does the stun last
        self.damage = 4           # Amount of damage dealt
        
    def attack(self):
        Tower.attack(self, [self.applyStun] )
        
    def applyStun(self):
        self.target.stun( self.stunDuration )
        
# Parent class for enemies that travel along the path
class Enemy(DirectObject):
    def __init__(self, parent, startingBlock, map, model):
        self.map = map                      # The map itself - needed for finding the path
        self.startingBlock = startingBlock  # The block the enemy is traveling to
        self.direction = 0                  # The direction the enemy is traveling (Right = 0, Down = 1, Left = 2, Up = 3)
        self.maxHealth = self.health        # The starting health of the enemy
        self.maxMoveSpeed = 1               # How many seconds it takes the enemy to move from one block to another
        self.moveSpeed = self.maxMoveSpeed  # The current movespeed
        self.isActive = 1                   # Whether the enemy is alive and moving
        self.index = -1                     # The index of the enemy
        self.distanceTravelled = 0
        
        # Load and place the model
        self.eNode = parent.attachNewNode('enemyBaseNode')
        self.eNode.setPos( startingBlock.getPos() )
        
        self.model = loader.loadModel( 'models/' + model )
        self.model.reparentTo( self.eNode )
        
        # Setup the rest of what the enemy needs
        self.setupCollision()
        self.setupHealthBar()
        
    def move(self, task):
        dist = self.moveSpeed * globalClock.getDt()
        deltaPos = DIRECTION_TO_VECTOR[self.direction] * dist
        self.eNode.setPos( self.eNode.getPos() + deltaPos )
        
        self.distanceTravelled += dist
        if( self.distanceTravelled >= 1.0 ):
            self.moveToNextBlock( self.currentBlock )
            self.distanceTravelled = 0
            return task.done
        
        return task.cont
        
    # Tells the enemy to start moving along the path
    def moveToEnd(self):
        self.moveToNextBlock( self.startingBlock )
        
    def moveToNextBlock(self, currentBlock):
        # If we've reached the last block, don't move anymore;
        # otherwise, find the next block in the path and start moving
        if( currentBlock.isType(EndBlock) ): 
            taskMgr.doMethodLater( self.moveSpeed, self.remove, 'remove' )
        else:
            self.currentBlock = self.findNextBlock( currentBlock )
            
            # Start moving
            taskMgr.add( self.move, 'move' + str(self.index) )
        
    # Locates the next block on the path based upon the enemy's current location
    def findNextBlock(self, currentBlock):
        (row, ignore, col) = currentBlock.index.partition(' ')
        row = int(row)
        col = int(col)
        dir = self.direction
        nextBlock = 0
        
        if( dir > -1 ):
            dir = (dir - 1) % 4
            
            for i in range(4):
                if( dir == 0 ):
                    nextBlock = self.map[row][col + 1]
                elif( dir == 1 ):
                    nextBlock = self.map[row - 1][col]
                elif( dir == 2 ):
                    nextBlock = self.map[row][col - 1]
                else:
                    nextBlock = self.map[row + 1][col]
                
                if( nextBlock.isType(PathBlock) or nextBlock.isType(EndBlock) ):
                    self.direction = dir
                    break
                
                dir = (dir + 1) % 4
                nextBlock = 0
                
        return nextBlock
        
    # Finds the first path block after the start block
    def findFirstPathBlock(self, currentBlock):
        (row, ignore, col) = currentBlock.index.partition(' ')
        row = int(row)
        col = int(col)
        dir = 0
        
        for dir in range(4):
                if( dir == 0 ):
                    nextBlock = self.map[row][col + 1]
                elif( dir == 1 ):
                    nextBlock = self.map[row - 1][col]
                elif( dir == 2 ):
                    nextBlock = self.map[row][col - 1]
                else:
                    nextBlock = self.map[row + 1][col]
                
                if( nextBlock.isType(PathBlock) ):
                    self.direction = dir
                    break
                
                nextBlock = 0
        
        return nextBlock
    
    # Removes the enemy once it has died or reached the end block
    def remove(self, task = None):
        #self.moveLerp.finish()
        self.isActive = 0
        self.eNode.removeNode()
        self.sphere.removeNode()
        taskMgr.remove('move' + str(self.index))
        messenger.send('enemy_removed', [self])
        
    # Sets up collision geometry so towers can find the enemy
    def setupCollision(self):
        self.sphere = self.eNode.attachNewNode( CollisionNode('object') )
        self.sphere.node().addSolid( CollisionSphere(0, 0, 0, 0.1) )
        self.sphere.node().setFromCollideMask( BitMask32.allOff() )
        self.sphere.node().setIntoCollideMask( BitMask32(2) )
        
    def setIndex(self, index):
        self.sphere.setTag('index', str(index) )
        self.index = index
        
    # Creates the health bar above the enemy
    def setupHealthBar(self):
        self.hpBar = DirectWaitBar( text = "", value = 100.0, pos = (0, 0, 1.5), scale = 0.3, barColor = Vec4(1, 0, 0, 1) )
        self.hpBar.setBillboardPointEye() 
        self.hpBar.reparentTo(self.eNode)
        #self.hpBar.clearColor()
        
    # Decreases the health of the enemy by the damage it takes
    def takeDamage(self, damage):
        self.health -= damage
        self.hpBar['value'] = (1.0 * self.health) / self.maxHealth * 100
        if( self.health <= 0 ):
            self.remove()
            
    def slow(self, fraction, duration):
        self.moveSpeed = self.maxMoveSpeed * fraction
        self.model.setColor( SLOW_COLOR )
        
        taskMgr.remove( 'removeSlow' + str(self.index) )
        taskMgr.doMethodLater( duration, self.removeSlow, 'removeSlow' + str(self.index) )
        
    def removeSlow(self, task = None):
        self.moveSpeed = self.maxMoveSpeed
        self.model.clearColor()
        
    def stun(self, duration):
        self.moveSpeed = 0
        self.model.setColor( STUN_COLOR )
        
        taskMgr.remove( 'removeStun' + str(self.index) )
        taskMgr.doMethodLater( duration, self.removeStun, 'removeStun' + str(self.index) )
        
    def removeStun(self, task = None):
        self.moveSpeed = self.maxMoveSpeed
        self.model.clearColor()
        
class Pawn(Enemy):
    def __init__(self, parent, startingBlock, map):
        self.health = 10
        Enemy.__init__(self, parent, startingBlock, map, 'pawn')
        #self.model.setColor( Vec4(1, 0, 0, 0.5) )
        
        
class Bishop(Enemy):
    def __init__(self, parent, startingBlock, map):
        self.health = 50
        Enemy.__init__(self, parent, startingBlock, map, 'bishop')
        #self.model.setColor( Vec4(0, 1, 0, 0.5) )
        
        
class Rook(Enemy):
    def __init__(self, parent, startingBlock, map):
        self.health = 20
        Enemy.__init__(self, parent, startingBlock, map, 'rook')
        #self.model.setColor( Vec4(0, 0, 1, 0.5) )
        