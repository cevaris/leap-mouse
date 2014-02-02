#!/usr/bin/env python

import imp
from pymouse import PyMouse
imp.load_source('Leap', 'lib/Leap.py')

import Leap, sys
from Leap import CircleGesture, KeyTapGesture, ScreenTapGesture, SwipeGesture
import time



class State:
    def __init__(self,name, state):
        self.name = name
        self.state = state
    def eq(self, state2):
        return self.state == state2.state
    def __str__(self):
        return "%s %s" % (self.name or 'None', str(self.state))
    

UP =        State('UP',(0, 1))
UPRIGHT =   State('UPRIGHT',(1, 1))
RIGHT =     State('RIGHT',(1, 0))
DOWNRIGHT = State('DOWNRIGHT',(1, -1))
DOWN =      State('DOWN',(0, -1))
DOWNLEFT =  State('DOWNLEFT',(-1, -1))
LEFT =      State('LEFT',(-1, 0))
UPLEFT =    State('UPLEFT',(-1, 1))
CENTER =    State('CENTER',(0,0))

SPEED = 5
ZERO_THRESHOLD = 50.0
MOUSE = PyMouse()

LEFT_CLICK   = 1
MIDDLE_CLICK = 2
RIGHT_CLICK  = 3


def mousemove(deltax,deltay):
    x,y = MOUSE.position()
    w,h = MOUSE.screen_size()

    nextx, nexty = deltax+x, deltay+y
    
    if nextx < 0: nextx = 0
    if nextx > w: nextx = w
    if nexty < 0: nexty = 0
    if nexty > h: nexty = h

    MOUSE.move(nextx,nexty)

def mouse_click(type):
    x,y = MOUSE.position()
    MOUSE.click(x,y,type)

def render(state):
    """ Converted to default screen layout, where top,left is 0,0 in coordinate plane """
    if    state.eq(UP):        mousemove(0,-SPEED)
    elif  state.eq(UPRIGHT):   mousemove(SPEED,-SPEED)
    elif  state.eq(RIGHT):     mousemove(SPEED,0)
    elif  state.eq(DOWNRIGHT): mousemove(SPEED,SPEED)
    elif  state.eq(DOWN):      mousemove(0,SPEED)
    elif  state.eq(DOWNLEFT):  mousemove(-SPEED,SPEED)
    elif  state.eq(LEFT):      mousemove(-SPEED,0)
    elif  state.eq(UPLEFT):    mousemove(-SPEED,-SPEED)
    else: pass # Center, Do nothing


def calc_state(x, y, z):
    
    # Normalize Xaxis
    if abs(x) < 20:
        x = 0
    elif x < 0:
        x = -1
    elif x > 0:
        x = 1
    
    # Normalize Yaxis
    if 120 < y and y < 140:
        y = 0
    elif y < 120:
        y = -1
    elif y > 140:
        y = 1

    now = State(None,(x,y))  
    state = None
    
    if    now.eq(UP):        state = UP
    elif  now.eq(UPRIGHT):   state = UPRIGHT
    elif  now.eq(RIGHT):     state = RIGHT
    elif  now.eq(DOWNRIGHT): state = DOWNRIGHT
    elif  now.eq(DOWN):      state = DOWN
    elif  now.eq(DOWNLEFT):  state = DOWNLEFT
    elif  now.eq(LEFT):      state = LEFT
    elif  now.eq(UPLEFT):    state = UPLEFT
    else: state = CENTER

    return state


class SampleListener(Leap.Listener):
    def on_init(self, controller):
        print "Initialized"

    def on_connect(self, controller):
        print "Connected"

        # Enable gestures
        controller.enable_gesture(Leap.Gesture.TYPE_CIRCLE);
        controller.enable_gesture(Leap.Gesture.TYPE_KEY_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SCREEN_TAP);
        controller.enable_gesture(Leap.Gesture.TYPE_SWIPE);

    def on_disconnect(self, controller):
        # Note: not dispatched when running in a debugger.
        print "Disconnected"

    def on_exit(self, controller):
        print "Exited"

    def on_frame(self, controller):
        # Get the most recent frame and report some basic information
        frame = controller.frame()

        print "Frame id: %d, timestamp: %d, hands: %d, fingers: %d, tools: %d, gestures: %d" % (
              frame.id, frame.timestamp, len(frame.hands), len(frame.fingers), len(frame.tools), len(frame.gestures()))

        if not frame.hands.is_empty:
            # Get the first hand
            hand = frame.hands[0]

            # Check if the hand has any fingers
            fingers = hand.fingers
            if not fingers.is_empty:
                # Calculate the hand's average finger tip position
                avg_pos = Leap.Vector()
                for finger in fingers:
                    avg_pos += finger.tip_position
                avg_pos /= len(fingers)
                print "Hand has %d fingers, average finger tip position: x=%.2f, y=%.2f z=%.2f" % ( len(fingers), avg_pos[0],avg_pos[1],avg_pos[2] )
                
                render(calc_state(avg_pos[0],avg_pos[1],avg_pos[2]))







            # Get the hand's sphere radius and palm position
            print "Hand sphere radius: %f mm, palm position: %s" % (hand.sphere_radius, hand.palm_position)

            # Get the hand's normal vector and direction
            normal = hand.palm_normal
            direction = hand.direction

            # Calculate the hand's pitch, roll, and yaw angles
            print "Hand pitch: %f degrees, roll: %f degrees, yaw: %f degrees" % (
                direction.pitch * Leap.RAD_TO_DEG,
                normal.roll * Leap.RAD_TO_DEG,
                direction.yaw * Leap.RAD_TO_DEG)

            # Gestures
            for gesture in frame.gestures():
                if gesture.type == Leap.Gesture.TYPE_CIRCLE:
                    circle = CircleGesture(gesture)

                    # Determine clock direction using the angle between the pointable and the circle normal
                    if circle.pointable.direction.angle_to(circle.normal) <= Leap.PI/4:
                        clockwiseness = "clockwise"
                    else:
                        clockwiseness = "counterclockwise"

                    # Calculate the angle swept since the last frame
                    swept_angle = 0
                    if circle.state != Leap.Gesture.STATE_START:
                        previous_update = CircleGesture(controller.frame(1).gesture(circle.id))
                        swept_angle =  (circle.progress - previous_update.progress) * 2 * Leap.PI

                    print "Circle id: %d, %s, progress: %f, radius: %f, angle: %f degrees, %s" % (
                            gesture.id, self.state_string(gesture.state),
                            circle.progress, circle.radius, swept_angle * Leap.RAD_TO_DEG, clockwiseness)

                if gesture.type == Leap.Gesture.TYPE_SWIPE:
                    swipe = SwipeGesture(gesture)
                    print "Swipe id: %d, state: %s, position: %s, direction: %s, speed: %f" % (
                            gesture.id, self.state_string(gesture.state),
                            swipe.position, swipe.direction, swipe.speed)

                if gesture.type == Leap.Gesture.TYPE_KEY_TAP:
                    keytap = KeyTapGesture(gesture)
                    print "Key Tap id: %d, %s, position: %s, direction: %s" % (
                            gesture.id, self.state_string(gesture.state),
                            keytap.position, keytap.direction )
                    mouse_click(LEFT_CLICK)

                if gesture.type == Leap.Gesture.TYPE_SCREEN_TAP:
                    screentap = ScreenTapGesture(gesture)
                    print "Screen Tap id: %d, %s, position: %s, direction: %s" % (
                            gesture.id, self.state_string(gesture.state),
                            screentap.position, screentap.direction )
                    mouse_click(LEFT_CLICK)

        if not (frame.hands.is_empty and frame.gestures().is_empty):
            print ""

    def state_string(self, state):
        if state == Leap.Gesture.STATE_START:
            return "STATE_START"

        if state == Leap.Gesture.STATE_UPDATE:
            return "STATE_UPDATE"

        if state == Leap.Gesture.STATE_STOP:
            return "STATE_STOP"

        if state == Leap.Gesture.STATE_INVALID:
            return "STATE_INVALID"

def main():
    # Create a sample listener and controller
    listener = SampleListener()
    controller = Leap.Controller()

    # Allow capture of frames when app not in focus
    controller.set_policy_flags(Leap.Controller.POLICY_BACKGROUND_FRAMES);

    # Have the sample listener receive events from the controller
    controller.add_listener(listener)


    # Keep this process running until Enter is pressed
    print "Press Enter to quit..."
    sys.stdin.readline()

    # Remove the sample listener when done
    controller.remove_listener(listener)


    # width = NSScreen.mainScreen().frame().size.width
    # height = NSScreen.mainScreen().frame().size.height
    # center = [width,height]
    # print width, height


if __name__ == "__main__":
    main()
