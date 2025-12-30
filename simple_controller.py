import asyncio
from aioconsole import ainput
from mavsdk import System
#position for absolute postion; velocity for relative position
from mavsdk.offboard import OffboardError, VelocityNedYaw, PositionNedYaw
from mavsdk.action import ActionError
#monitor key press
import curses
import time
from Mavlink_connection import PX4

class Simple_controller():
    px4=PX4()
    usage_str = """
        Usage:
        a    print all actions
        c    controller mode
        i    print drone status
        """
    index_action=0
    is_hold=False

    async def establish_connection(self):
        try:
            is_connected = await self.px4.isConnected()
            while not is_connected:
                await self.px4.connect_to_drone()
                is_connected = await self.px4.isConnected()
        except RuntimeError as e:
            print(f"Error in establish_connection(): {e}")
            await self.px4.connect_to_drone()
            await asyncio.sleep(2)
        finally:
            try:
                while await self.px4.isConnected():
                    await self.run()
            except ActionError as e:
                print(f"ActionError: {e}")
                exit()
        
    async def isArmed(self)->bool:
        return await self.px4.isArmed()

    async def arm(self):
        try: 
            await self.px4.arm()
        except RuntimeError as e:
            print(f"Command Denied: {e}")
        
    async def takeoff(self, min_alt=0.3):
        try: 
            await self.px4.takeoff()
        except RuntimeError as e:
            print(f"Command Denied: {e}")

    async def hold(self):
        try: 
            await self.px4.hold()
        except RuntimeError as e:
            print(f"Command Denied: {e}")
        except AttributeError as e:
            print("Drone is not initialized")
        except asyncio.CancelledError as e:
            print(f"Task cancelled: {e}")
        finally:
            self.is_hold=False
            print("Hold Done")

    async def land(self):
        try: 
            await self.px4.land()
        except RuntimeError:
            print("Command Denied")

    async def pitch(self, p):
        await self.px4.pitch(p)

    async def roll(self, r):
        await self.px4.roll(r)

    async def throttle(self, t):
        await self.px4.throttle(t)

    async def yaw(self, y):
        await self.px4.yaw(y)

    async def manual_control(self, pitch, roll, throttle, yaw):
        await self.px4.manual_control(pitch, roll, throttle, yaw)

    async def is_manualControl_enabled(self) -> bool:
        return await self.px4.is_manualControl_enabled()

    async def key_controller(self, stdscr):
        if not await self.is_manualControl_enabled():
            return
        curses.curs_set(0)
        stdscr.nodelay(True)
        stdscr.clear()
        STEP=0.6
        while True:
            key=stdscr.getch()

            #reset motion
            pitch = roll = yaw = 0.0
            throttle=0.5
            
            if key != -1:
                if key in [ord('w'), ord('W')]:
                    pitch = STEP
                elif key in [ord('s'), ord('S')]:
                    pitch = -STEP
                elif key in [ord('a'), ord('A')]:
                    roll = -STEP
                elif key in [ord('d'), ord('D')]:
                    roll = STEP

                elif key in [ord('i'), ord('I')]:
                    throttle = 0.8
                elif key in [ord('k'), ord('K')]:
                    throttle = 0.2
                elif key in [ord('j'), ord('J')]:
                    yaw = -STEP
                elif key in [ord('l'), ord('L')]:
                    yaw = STEP

                elif key in [ord('q'), ord('Q')]:
                    # Quit cleanly
                    await self.throttle(0.25)
                    key=-1
                    break

            await self.manual_control(pitch, roll, throttle, yaw)

            stdscr.addstr(0, 0, "Drone Keyboard Controller (press 'q' to quit)")
            stdscr.addstr(2, 0, f"Pitch:    {pitch:+.2f}")
            stdscr.addstr(3, 0, f"Roll:     {roll:+.2f}")
            stdscr.addstr(4, 0, f"Throttle: {throttle:+.2f}")
            stdscr.addstr(5, 0, f"Yaw:      {yaw:+.2f}")
            stdscr.refresh()
            #stdscr.addstr(0,0,"Press w,s to pitch; a,d to roll; up,down to throttle; left, right to yaw; Press q or ESC to quit")

            await asyncio.sleep(0.05)  # 20 Hz update rate

    async def make_user_choose_action(self):
        index_action_str = await ainput("\nWhich action do you want? [1..4] >>> ")
        if index_action_str == '':
            raise ValueError()
        index_action = int(index_action_str)
        if index_action < 1 or index_action > 4:
            raise ValueError()

        return index_action

    async def run(self):
        if self.is_hold:
            await self.px4.hold()
            self.is_hold=False
        entered_input = await ainput(self.usage_str)
        if entered_input == "a":
            print("\n=== Possible Actions ===\n")
            print("""
            1. arm
            2. takeoff
            3. hold
            4. land
            """)
            try:
                index_action = await self.make_user_choose_action()
            except ValueError:
                print("Invalid index")
                #continue

            if index_action == 1:
                await self.arm()
            elif index_action==2:
                await self.takeoff()
            elif index_action==3:
                print("Holding...")
                self.is_hold=True
                #continue
            elif index_action==4:
                await self.land()
            else:
                print("Invaid input")
            print(f"Finish {index_action}!")
        elif entered_input == "c":
            print("\n=== manual control mode ===\n")
            try:
                if not await self.isArmed():
                    print("Drone is not in air, armming...")
                    await self.px4.arm()
            except RuntimeError as e:
                print("Drone is not initialed")
            finally:
                await curses.wrapper(self.key_controller)

        elif entered_input=='i':
            try:
                all_params = await self.px4.param.get_all_params()
                for param in all_params.int_params:
                    print(f"{param.name}: {param.value}")
            except RuntimeError as e:
                print("Drone is not initialed")
        else:
            print("Invalid input!")
            #continue
        
if __name__ == "__main__":
    controller =Simple_controller()
    asyncio.run(controller.establish_connection())
