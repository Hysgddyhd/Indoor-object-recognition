import os
import re
import subprocess
import math

class Model():
    X_Y_RANGE=0.20
    Z_RANGE=0.08
    pos = []

    def __init__(self):
        self.name=""
        self.setup()

    def setup(self):
        self.name = os.popen('gz model --list 2>/dev/null | grep "x500"').read().split('-')[1].strip()
        self.updatePos()
        self.getPos()

    def getName(self):
        return self.name

    def getPos(self)-> list:
        self.updatePos()
        return self.pos

    #def gotoPos(self, x, y, z, r, p, y):
        


    def updatePos(self):
        new_pos=[]
        pattern = r'\[\s*([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s+([-+]?\d+\.\d+)\s*\]'
        try:
    # We use subprocess.check_output to get the result as a string
    # shell=True allows the use of pipes and redirects like '2>/dev/null'
            output = subprocess.check_output(
                f'gz model -m {self.name} -p 2>/dev/null', 
                shell=True, 
                timeout=0.80,
                text=True
            )
            
        except subprocess.TimeoutExpired:
            output=""
            print(f"Command timed out after 3.0s")
            if self.pos==None:
                self.updatePos()
            return
        except subprocess.CalledProcessError:
            output=""
            print("Command failed")
            if self.pos==None:
                self.updatePos()
            return

        all_matches = re.findall(pattern, output)
        for item in all_matches:
            for string in item:
                new_pos.append(float(string))
        self.pos=new_pos
       

    async def gotoX(self, controller, x):
        #if not await controller.isArmed():
        #    await controller.arm()
        await controller.manual_control(0,0,0.5,0)
        if abs(self.pos[0]-x)<self.X_Y_RANGE:
            print(f"current pose: ({self.pos[0]}, {self.pos[1]}, {self.pos[2]})")
        else:
            while abs(self.pos[0]-x)>self.X_Y_RANGE:
                difference = abs(self.pos[0]-x)
                speed = 0.35 if difference>4 else abs(difference-self.X_Y_RANGE)*0.15/(4-self.X_Y_RANGE)+0.15
                print(f"Pitch speed: {speed if self.pos[0]<x else -speed}")    
                await controller.pitch(p=speed if self.pos[0]<x else -speed, time=0.05)
                self.getPos()
                print(f"current pose: ({self.pos[0]}, {self.pos[1]}, {self.pos[2]})")
        print(f"Drone has gone to X {x}")
    
    async def gotoY(self, controller, y):
        #if not await controller.isArmed():
        #    await controller.arm()
        await controller.manual_control(0,0,0.5,0)
        if abs(self.pos[1]-y)<self.X_Y_RANGE:
            print(f"current pose: ({self.pos[0]}, {self.pos[1]}, {self.pos[2]})")
        else:
            while abs(self.pos[1]-y)>self.X_Y_RANGE:
                difference = abs(self.pos[1]-y)
                speed = 0.35  if difference>4 else abs(difference-self.X_Y_RANGE)*0.15/(4-self.X_Y_RANGE)+0.15
                print(f"Roll speed: {speed if self.pos[1]<y else -speed}")    
                await controller.roll(r=-speed if self.pos[1]<y else speed, time=0.05)
                self.getPos()
                print(f"current pose: ({self.pos[0]}, {self.pos[1]}, {self.pos[2]})")
        print(f"Drone has gone to Y {y}")


    async def gotoZ(self, controller, z):
        #if not await controller.isArmed():
        #    await controller.arm()
        await controller.manual_control(0,0,0.5,0)
        if abs(self.pos[2]-z)<self.Z_RANGE:
            print(1)
            print(f"current pose: ({self.pos[0]}, {self.pos[1]}, {self.pos[2]})")
        else:
            while abs(self.pos[2]-z)>self.Z_RANGE:
                difference = abs(self.pos[2]-z)
                speed = 0.35 if difference>1.2 else abs(difference-self.Z_RANGE)*0.15/(1.2-self.Z_RANGE)+0.08
                print(f"Throttle speed: {0.53+speed if self.pos[2]<z else 0.5-speed}")
                await controller.throttle(t=0.53+speed if self.pos[2]<z else 0.5-speed, time=0.05)
                self.getPos()
                print(f"current pose: ({self.pos[0]}, {self.pos[1]}, {self.pos[2]})") 
        print(6)
        print(f"Drone has gone to z/height {z}")
    

    async def yaw(self, controller,  y):
        range = 0.05
        await controller.manual_control(0,0,0.5,0)
        self.getPos()
        y=y%math.pi
        proposed_distance_if_travel_positive=abs(-2*math.pi+y-self.pos[5])
        #if abs(self.pos[5]-y>math.pi):
        if proposed_distance_if_travel_positive<2*math.pi and proposed_distance_if_travel_positive>math.pi:
            print(f"Go by counter clock direction")
            while abs(self.pos[5]-y)>range:
                await controller.yaw(-0.35, time=0.05)
                self.getPos()
                print(f"current angle: {self.pos[5]}")
        else:
            print(f"Go by clock direction")
            while abs(self.pos[5]-y)>range:
                await controller.yaw(0.35, time=0.05)
                self.getPos()
                print(f"current angle: {self.pos[5]}")
        
        print(f"Drone has rotate to target angle {y}")

        #if(self.pos[])

    async def gotoXYZ(self, controller, x, y, z):
        await(self.gotoZ(controller, z))
        await(self.yaw(controller, 0))

        await(self.gotoX(controller, x))
        await(self.yaw(controller, 0))

        await(self.gotoY(controller, y))
        print(f"Drone is at destination: {self.pos[0]}, {self.pos[1]}, {self.pos[2]}")


if __name__=='__main__':
    drone=Model()
    print(drone.getPos())
