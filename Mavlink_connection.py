from mavsdk import System
from aioconsole import ainput
import asyncio
from mavsdk.offboard import OffboardError, VelocityNedYaw, PositionNedYaw
import time


class PX4():
    px4=System()
    stop_event=asyncio.Event()

    async def connect_to_drone(self):
        await self.px4.connect(system_address="udpin://0.0.0.0:14540")
        print("Waiting for drone to connect...")
        async for state in self.px4.core.connection_state():
            if state.is_connected:
                print("Drone discovered!")
                break
        await self.initial_pos()
        print("Conntected")
            

    async def initial_pos(self):
        async for health in self.px4.telemetry.health():
            if health.is_gyrometer_calibration_ok and \
            health.is_accelerometer_calibration_ok and \
            health.is_magnetometer_calibration_ok:
                
                # Additional check: wait for global position (GPS) lock
                async for gps_info in self.px4.telemetry.gps_info():
                    if gps_info.num_satellites >= 6: # or use another minimum threshold
                        print("✅ System Health: All sensors calibrated and sufficient GPS lock.")
                        return # Exit the function once ready
                    else:
                        print(f"Waiting for sufficient GPS satellites (Current: {gps_info.num_satellites})...")
                        break # Break the inner loop, wait 1s, and check health again
                
            else:
                print("❌ System Health: Waiting for sensor calibrations to be OK...")

        await asyncio.sleep(1)
        await self.px4.telemetry.set_rate_imu(200.0)
        await self.px4.offboard.set_velocity_ned(VelocityNedYaw(0.0, 0.0, 0.0, 0.0))

    async def isConnected(self)->bool:
        #try: 
        isConnected = self.px4.core is not None
        return isConnected
        #except RuntimeError as e:
        #    print(f"Error in isConnected(): {e}")
        #    return False

    async def isArmed(self) -> bool:
        async for is_arm in self.px4.telemetry.armed():
            return is_arm
            
    async def getStatus(self) -> list:
        status=[]
        try:
            all_params = await self.px4.param.get_all_params()
            for param in all_params.int_params:
                status.append(f"{param.name}: {param.value}")
        except RuntimeError as e:
            print("Drone is not initialed")
        return status

    async def arm(self):
        print("Arming...")
        await self.px4.action.arm()
        print("OK")
        
    async def takeoff(self, duration=2):
        start_time=time.perf_counter()
        async for isArm in self.px4.telemetry.armed():
            if not isArm:
                print("Not armed")
                return()
            else:
                print("Starting to takeoff")
                break
        async for pos in self.px4.telemetry.position():
            if time.perf_counter()-start_time < duration:
                await self.px4.action.takeoff()
            else:
                break
            await asyncio.sleep(0.1)
        print(f"Current altitude: {pos.absolute_altitude_m} m")

    def clearStopEvent(self):
        self.stop_event.clear()

    async def holding_task(self):
        hold_time=time.monotonic()
        while not self.stop_event.is_set():
            if self.px4.telemetry.in_air() and self.hold:
                await self.px4.action.hold()
                #print("Holding...")
            else:
                raise asyncio.CancelledError
            await asyncio.sleep(0.1)    


    async def hold(self):
        self.clearStopEvent()
        hold_task = asyncio.create_task(self.holding_task())   
        await ainput("Type something to stop:\n")  
        self.stop_event.set()
        await hold_task
        print("!Hold done")

    async def land(self):
        async for in_air in self.px4.telemetry.in_air():
            if in_air:
                print("Starting to land")
                await self.px4.action.land()
                break
            else:
                print("Rejected! already on land.")
                break
        #controller in velocity mode    
    
    async def is_manualControl_enabled(self) -> bool:
        try:
            await self.px4.manual_control.set_manual_control_input(float(0), float(0), float(0.5), float(0))
            await self.px4.manual_control.start_position_control()
            return True
        except ManualControlError as e:
            print(f"ManualControlError: {e}")
            return False



#manual control

    async def pitch(self, p, time=0.1):
        await self.px4.manual_control.set_manual_control_input(p, 0, 0.5, 0)
        await asyncio.sleep(time)

    async def roll(self, r,time=0.1):
        await self.px4.manual_control.set_manual_control_input(0, r, 0.5, 0)
        await asyncio.sleep(time)

    async def throttle(self, t, time=0.1):
        await self.px4.manual_control.set_manual_control_input(0, 0, t, 0)
        await asyncio.sleep(time)

    async def yaw(self, y, time=0.1):
        await self.px4.manual_control.set_manual_control_input(0, 0, 0.5, y)
        await asyncio.sleep(time)

    async def manual_control(self, pitch, roll, throttle, yaw, time=0.1):
        await self.px4.manual_control.set_manual_control_input(pitch, roll, throttle, yaw)
        await asyncio.sleep(time)

async def main():
    # Assume 'px4' object is initialized and connected here
    # For demonstration, we'll use a placeholder class:
    px4 =PX4()
    await px4.connect_to_drone()
    status = await px4.getStatus()
    await asyncio.sleep(0.1) # Simulate waiting for status data
    print(status)
            
if __name__ == "__main__":
    asyncio.run(
        main()
    )
