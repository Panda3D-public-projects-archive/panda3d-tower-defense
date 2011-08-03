import settings

from direct.showbase.DirectObject import DirectObject
from panda3d.core import VBase3

class RTS_Camera( DirectObject ):
    def __init__(self):
        self.floater = render.attachNewNode('cam_floater')  # Used to create an angle
        #self.floater.setPos(5, 5, 0)

        self.tolerance = 10             # How many pixels from the edge of the window
        self.cameraMoveDist = 14        # How many units to move the camera
        self.cameraZoomDist = 4         # How many units to zoom the camera
        self.cameraZ = 30               # Default starting height of camera
        self.cameraZBounds = [4, 60]    # Lower and upper bounds of camera height

        base.disableMouse()                 # Turn off default mouse control
        base.camera.setPos(0, -10, 15)      # Default camera position
        base.camera.lookAt(self.floater)    # Make the camera look at the floater (creates angle)

        self.accept( 'wheel_up', self.zoom, [1] )       # Listen for mouse scrolling
        self.accept( 'wheel_down', self.zoom, [-1] )    # for zooming
        
        self.accept( 'arrow_left', self.moveCamera, [-3, 0])
        self.accept( 'arrow_right', self.moveCamera, [3, 0])
        self.accept( 'arrow_up', self.moveCamera, [0, 3])
        self.accept( 'arrow_down', self.moveCamera, [0, -3])

    # This gets run every frame by the game engine.
    # Here we find the position of the cursor - if it is
    # near the edges of the screen (within a tolerance),
    # we will update the position of the camera
    def handleMouseInput(self):
        xDir = 0
        yDir = 0

        # Get the position of the cursor if it is in the window
        if( base.mouseWatcherNode.hasMouse() or 1 ):
            md = base.win.getPointer(0)
            x = md.getX()
            y = md.getY()

            # If the cursor is on the edges, move the camera
            if( x + self.tolerance > settings.WIDTH ):
                xDir = 1
            elif( x < self.tolerance ):
                xDir = -1
            if( y + self.tolerance > settings.HEIGHT ):
                yDir = -1
            elif( y < self.tolerance ):
                yDir = 1

            self.moveCamera( xDir, yDir )

    def moveCamera(self, x, y):
        dir = VBase3(x, y, 0)
        deltaPos = dir * self.cameraMoveDist * globalClock.getDt()

        self.floater.setPos( self.floater.getPos() + deltaPos )
        base.camera.setPos( base.camera.getPos() + deltaPos )

    # Determines the vector from the camera to the floater and moves the
    # camera closer to or farther from the floater along the vector
    def zoom(self, dir):
        camToFloater = self.floater.getPos() - base.camera.getPos()
        camToFloater.normalize()
        camToFloater *= dir * self.cameraZoomDist

        newPos = base.camera.getPos() + camToFloater
        z = newPos.getZ()

        if( z < self.cameraZBounds[1] and z > self.cameraZBounds[0]):
            base.camera.setPos(newPos)