from os import system
import sys
import re
import threading
import time
import subprocess
from Thread import *

distro_id_line_pattern = "Distributor ID:.+?(?=n)."
process = subprocess.Popen(["lsb_release", "-a"], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
host_sys_info = process.communicate()
OS_ID_LINE = re.findall(distro_id_line_pattern, str(host_sys_info[0]))
distro_ID = OS_ID_LINE[0].replace("Distributor ID:\\t", '')
distro_ID = distro_ID.replace("\\n", '')

if distro_ID == "Raspbian":
    from Servo import *

# The terminal to control the part of LEG include:
#               ____    
#       _______|    |_______
#      |L1                R1|
#      |                    |
#      |                    |
#      |                    |
#      |                    |
#      |                    |
#      |L2________________R2|
#
# * Hip joint:      [4, 7, 8, 11]   <=> [L1 L2 R1 R2]
# * Tibia joint:    [2, 5, 10, 13]  <=> [L1 L2 R1 R2]
# * Femur joint:    [3, 6, 9, 12]   <=> [L1 L2 R1 R2]

class RobotDogFreeNove:
    def __init__(self) -> None:
        self.ACTION = [
            'FORWARD',
            'BACKWARD',
            'TURNRIGHT',
            'TURNLEFT',
            'CALIBRATION',
            'CRAWLING',
            'FOLLOW'
        ]
        self.stability = [
            'UNSTABLE',
            'STABLE'
        ]
        self.STATE = {
            'IDLE':0,
            'MOVING':1,
            'STANDING':2,
            'SITTING':3,
            'FALLDOWN':4
        }
        self.hipJoint   = [4, 7, 8, 11]
        self.femurJoint = [2, 5, 10, 13]
        self.tibiaJoint = [3, 6, 8, 12]
        self.current_position = {   "HIP"   : [90, 90, 90, 90],
                                    "FEMUR" : [90, 90, 90, 90],
                                    "TIBIA" : [90, 90, 90, 90]}
        self.hipMovementAngularVector       = [90, 90, 90, 90]
        self.femureMovementAngularVector    = [90, 90, 90, 90]
        self.tibiaMovementAngularVector     = [90, 90, 90, 90]
        self.minimumAngleRotation = 10  #(degrees) will be remove when angle calculation is stable
        self.minimumDistance = 5        #(cm) will be remove when the calculation for distance of leg movement is stable 
        self.currentState = self.STATE['SITTING']
        self.minimuDisplacement = 1

    def readyToAction(self, action):
        if action == 'STANDING':
            HipSetupAngle   = 20
            FemurSetupAngle = 0
            TibiaSetupAngle = 50
            self.currentState = self.ACTION['STANDING']    
        if action == "SITTING":
            HipSetupAngle   = 0
            FemurSetupAngle = 0
            TibiaSetupAngle = 0
            self.currentState = self.ACTION['SITTING']

        self.current_position["HIP"]        = self.hipMovementAngularVector
        self.current_position["FEMUR"]      = self.femureMovementAngularVector
        self.current_position["TIBIA"]      = self.tibiaMovementAngularVector
        self.hipMovementAngularVector       = [90-HipSetupAngle, 90-HipSetupAngle, 90+HipSetupAngle, 90+HipSetupAngle]
        self.femureMovementAngularVector    = [90-FemurSetupAngle, 90-FemurSetupAngle, 90+FemurSetupAngle, 90+FemurSetupAngle]
        self.tibiaMovementAngularVector     = [90-TibiaSetupAngle, 90-TibiaSetupAngle, 90+TibiaSetupAngle, 90+TibiaSetupAngle]

    def setState(self, state):
        self.currentState = state

    def getState(self):
        return self.currentState

    def controlServo(self, partToMove, pilot):
        while(True):
            for index in range(4):        
                if(index > 2):
                    minimum_dis = -self.minimuDisplacement
                else:
                    minimum_dis = self.minimuDisplacement
                
                if(partToMove == "HIP"):
                    if (self.current_position["HIP"][index] > self.hipMovementAngularVector[index]):
                        self.current_position["HIP"][index] -= minimum_dis
                    elif (self.current_position["HIP"][index] < self.hipMovementAngularVector[index]):
                        self.current_position["HIP"][index] += minimum_dis
                    else:    
                        self.current_position["HIP"][index] = self.hipMovementAngularVector[index]

                    if distro_ID == "Raspbian":
                        pilot.setServoAngle(self.hipJoint[index], 
                                            self.current_position["HIP"][index])
                    
                    print("Hip Angle: ", self.current_position["HIP"][index])
                    
                if(partToMove == "FEMUR"):
                    if (self.current_position["FEMUR"][index] > self.femureMovementAngularVector[index]):
                        self.current_position["FEMUR"][index] -= minimum_dis
                    elif (self.current_position["FEMUR"][index] < self.femureMovementAngularVector[index]):
                        self.current_position["FEMUR"][index] += minimum_dis
                    else:    
                        self.current_position["FEMUR"][index] = self.femureMovementAngularVector[index]

                    if distro_ID == "Raspbian":
                        pilot.setServoAngle(self.femurJoint[index], 
                                            self.current_position["FEMUR"])
                    
                    print("Femur angle: ", self.current_position["FEMUR"][index])
                    
                if(partToMove == "TIBIA"):
                    if (self.current_position["TIBIA"][index] > self.tibiaMovementAngularVector[index]):
                        self.current_position["TIBIA"][index] -= minimum_dis
                    elif (self.current_position["TIBIA"][index] < self.tibiaMovementAngularVector[index]):
                        self.current_position["TIBIA"][index] += minimum_dis
                    else:    
                        self.current_position["TIBIA"][index] = self.tibiaMovementAngularVector[index]
                        
                    if distro_ID == "Raspbian":
                        pilot.setServoAngle(self.tibiaJoint[index], 
                                            self.current_position["TIBIA"])
                    
                    print("Tibia angle: ", self.current_position["TIBIA"][index])
            
            time.sleep(0.01)

    def activateLeg(self, robot):
        threadForHip    = threading.Thread(target=lambda x="HIP",   pilot = robot  :self.controlServo(x,pilot))
        threadForFemur  = threading.Thread(target=lambda x="FEMUR", pilot = robot  :self.controlServo(x,pilot))
        threadForTibia  = threading.Thread(target=lambda x="TIBIA", pilot = robot  :self.controlServo(x,pilot))
        threadForHip.start()
        threadForTibia.start()
        threadForFemur.start()
        time.sleep(1)
        stop_thread(threadForHip)
        stop_thread(threadForFemur)
        stop_thread(threadForTibia)
        
            
    def doAction(self, robot, action):
        if self.STATE[action] not in self.restrictMovement(self.currentState):
            return "Invalid action"
        if action == self.ACTION["SITTING"]:
            self.readyToAction("SITTING")
            self.activateLeg(robot)
        if action == self.ACTION["STANDING"]:
            self.readyToAction("STANDING")
            self.activateLeg(robot)


    def restrictMovement(self, action):
        # To restrict the movement of robot and avoid damages
        if action == self.ACTION['SITTING']:
            return [self.ACTION['STANDING'], self.ACTION['CRAWLING']]
        if action == self.ACTION['STANDING']:
            return [self.ACTION['MOVING'], self.ACTION['SITTING']]                

class RobotLeg2Joint(RobotDogFreeNove):

    def __init__(self) -> None:
        super().__init__()

        

if __name__ == "__main__":
    robot = RobotDogFreeNove()
    pilot = Servo()
    cmd = sys.argv[1]
    params = int(sys.argv[2])
    robot.doAction(pilot, "STANDING")

    pass