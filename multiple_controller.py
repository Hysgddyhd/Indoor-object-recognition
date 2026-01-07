import asyncio
from aioconsole import ainput
import csv
import io
import anyio
from mavsdk import System
from mavsdk.telemetry import LandedState
from mavsdk.offboard import OffboardError, VelocityNedYaw, PositionNedYaw
from mavsdk.action import ActionError
import time
import re
import curses
#import custom classes
from simple_controller import Simple_controller
from GZModel import Model

class Multi_controller(Simple_controller):
    gz_px4=Model()
    usage_str = """
        Usage:
        a    print all actions
        c    controller mode
        i    print drone status
        """

    async def _establish_connection(self):
        try:
            is_connected = await self.px4.isConnected()
            while not is_connected:
                await self.px4.connect_to_drone()
                is_connected = await self.px4.isConnected()
        except RuntimeError as e:
            print(f"Error in establish_connection(): {e}")
            await self.px4.connect_to_drone()
            await asyncio.sleep(2)

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
            except UnboundLocalError as e:
                print(f"Please enter something")
                await self.establish_connection()
            except IndexError:
                print(f"Pose is None")
                await self.establish_connection()

    async def gotoX(self, x):
        await self.gz_px4.gotoX(self.px4, x)
        self.is_hold=True#to hold drone

    async def gotoY(self, y):
        await self.gz_px4.gotoY(self.px4, y)
        self.is_hold=True#to hold drone

    async def gotoZ(self, z):
        await self.gz_px4.gotoZ(self.px4, z)
        self.is_hold=True#to hold drone 
    
    async def gotoXYZ(self, x, y, z):
        await self.gz_px4.gotoXYZ(self.px4, x, y, z)
        self.is_hold=True#to hold drone 

    async def yaw(self, y):
        await self.gz_px4.yaw(self.px4, y)
        self.is_hold=True

    async def patrol(self, csv_file):
        drone = self.px4.px4
        # Define a dictionary to map mode codes to their descriptions
        mode_descriptions = {
            0: "On the ground",
            10: "Initial climbing state",
            20: "Initial holding after climb",
            30: "Moving to start point",
            40: "Holding at start point",
            50: "Moving to maneuvering start point",
            60: "Holding at maneuver start point",
            70: "Maneuvering (trajectory)",
            80: "Holding at the end of the trajectory coordinate",
            90: "Returning to home coordinate",
            100: "Landing",
        }
        def get_current_waypoint(waypoints, time):
            return next((wp for wp in waypoints if time <= wp[0]), None)

       # Arm the drone
        print("-- Arming")
        await drone.action.arm()

        # Set the```python
        # Set the initial setpoint
        print("-- Setting initial setpoint")
        startSetpoint = PositionNedYaw(0.0, 0.0, 0.0, 0.0)
        await drone.offboard.set_position_ned(startSetpoint)

        # Start offboard mode
        print("-- Starting offboard")
        try:
            await drone.offboard.start()
        except OffboardError as error:
            print(f"Starting offboard mode failed with error code: {error._result.result}")
            print("-- Disarming")
            await drone.action.disarm()
            return

        # Read data from the CSV file
        async with await anyio.open_file(csv_file, "r", newline="") as csvfile:
            content = await csvfile.read()
        waypoints = [
            (
                float(row["t"]),
                float(row["px"]),
                float(row["py"]),
                float(row["pz"]),
                float(row["vx"]),
                float(row["vy"]),
                float(row["vz"]),
                float(row["ax"]),
                float(row["ay"]),
                float(row["az"]),
                int(row["mode"]),
            )
            for row in csv.DictReader(io.StringIO(content))
        ]

        print("-- Performing trajectory")
        total_duration = waypoints[-1][0]
        # Total duration is the time of the last waypoint
        t = 0  # Initialize time variable
        last_mode = 0
        while t <= total_duration:
            current_waypoint = get_current_waypoint(waypoints, t)
            if current_waypoint is None:
                # Reached the end of the trajectory
                break

            position = current_waypoint[1:4]
            velocity = current_waypoint[4:7]
            _acceleration = current_waypoint[7:10]  # unused
            mode_code = current_waypoint[-1]
            if last_mode != mode_code:
                # Print the mode number and its description
                print(" Mode number: " + f"{mode_code}, Description: {mode_descriptions[mode_code]}")
                last_mode = mode_code
            # set_position_velocity_acceleration_ned is not yet available
            # in the default build for MAVSDK-Python Installation with pip3
            # If you need to input acceleration,
            # you should build MAVSDK for yourself.
            await drone.offboard.set_position_velocity_ned(
                PositionNedYaw(*position, current_waypoint[10]),
                VelocityNedYaw(*velocity, current_waypoint[10]),
            )
            # await drone.offboard.set_position_velocity_acceleration_ned(
            #     PositionNedYaw(*position, current_waypoint[10]),
            #     VelocityNedYaw(*velocity, current_waypoint[10]),
            #     AccelerationNed(*acceleration, current_waypoint[10])
            # )

            timeStep = 0.1
            await asyncio.sleep(timeStep)  # Time resolution of 0.1 seconds
            t += timeStep

        print("-- Shape completed")

        print("-- Landing")
        await drone.action.land()

        async for state in drone.telemetry.landed_state():
            if state == LandedState.ON_GROUND:
                break

        print("-- Stopping offboard")
        try:
            await drone.offboard.stop()
        except Exception as error:
            print(f"Stopping offboard mode failed with error: {error}")

        print("-- Disarming")
        await drone.action.disarm()

    async def make_user_choose_action(self):
        index_action_str = await ainput("\nWhich action do you want? [0..9] >>> ")
        index_action = int(index_action_str)
        if index_action < 0 or index_action > 9:
            raise ValueError()
        return index_action

    async def getVaildDouble(self) -> float:
        user_input_str = await ainput("Please enter a floating-point number: ")
        # Attempt to convert the string input to a float
        validated_float = float(user_input_str)
        if validated_float<0:
            print("Too low")
            raise ValueError
        # If successful:
        print(f"\n✅ Input accepted. The float value is: {validated_float}")
        # --- Your subsequent code goes here ---
        # Use 'validated_float' for the action 4 logic
        return validated_float
            

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
            4. get pose
            5. goto X
            6. goto Y
            7. goto Z/Height
            8. patrol
            9. yaw
            0. land
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
                pose = self.gz_px4.getPos()
                print(f"Drone pose: ({pose[0], pose[1], pose[2]}, angle: {pose[5]})")
            elif index_action==5: #x
                try:
                    vaild_value = await self.getVaildDouble()
                except ValueError:
                    # If conversion fails (Invalid input):
                    print(f"\n🚨 Invalid input, it is not a valid floating-point number.")
                    print("The action will not be performed.")
                finally:
                    await self.gotoX(vaild_value)
            elif index_action==6: #y
                try:
                    vaild_value = await self.getVaildDouble()
                except ValueError:
                    # If conversion fails (Invalid input):
                    print(f"\n🚨 Invalid input, it is not a valid floating-point number.")
                    print("The action will not be performed.")
                finally:
                    await self.gotoY(vaild_value)
            elif index_action==7: #z
                try:
                    vaild_value = await self.getVaildDouble()
                except ValueError:
                    # If conversion fails (Invalid input):
                    print(f"\n🚨 Invalid input, it is not a valid floating-point number.")
                    print("The action will not be performed.")
                finally:
                    await self.gotoZ(vaild_value)
            elif index_action==8:
                    await self.patrol()
            elif index_action==9: #z
                try:
                    vaild_value = await self.getVaildDouble()
                except ValueError:
                    # If conversion fails (Invalid input):
                    print(f"\n🚨 Invalid input, it is not a valid floating-point number.")
                    print("The action will not be performed.")
                finally:
                    await self.yaw(vaild_value)

            elif index_action==0:
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
    controller = Multi_controller()
    asyncio.run(controller.establish_connection())
