import asyncio
from aioconsole import ainput
import curses
import time

class base_controller():
    height=0
    isArm=False
    is_hold=False
    usage_str = """
        Usage:
        a    print all actions
        """
    stop_event=asyncio.Event()

    async def arm(self):
        self.isArm=True
        await asyncio.sleep(1)
        
    async def takeoff(self, min_alt=0.2):
        if not self.isArm:
                print("Not armed")
                return()
        else:
            print("Starting to takeoff")
        while self.height<min_alt:
            self.height=self.height+0.1
            await asyncio.sleep(0.1)
        print(f"Current altitude: {self.height} m")

    async def hold(self, stop_event: asyncio.Event):
        hold_time=time.monotonic()
        while not stop_event.is_set():
            #print("Holding")
            await asyncio.sleep(1)
            if (int)(time.monotonic()-hold_time)%3==0:
                print(f"Holding, {time.monotonic()-hold_time:.1f} s")

    async def land(self):
        while self.height>0:
                self.height=self.height-0.1 if self.height>=0.1 else 0
                await asyncio.sleep(0.1)
        self.isArm=False
        print("Landed")
        
    async def make_user_choose_action(self):
        index_action_str = await ainput("\nWhich action do you want? [1..4] >>> ")
        index_action = int(index_action_str)
        if index_action < 1 or index_action > 4:
            raise ValueError()

        return index_action

    async def run(self):
        
        _tasks = [
            #asyncio.create_task(self.arm()),
            #asyncio.create_task(self.takeoff()),
            #asyncio.create_task(self.land()),
        ]
        while True:
            if self.is_hold:
                hold_task = asyncio.create_task(self.hold(self.stop_event))
                await ainput("Type something to stop:\n")  
                self.stop_event.set()
                await hold_task
                print("!Hold done")
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
                    continue

                if index_action == 1:
                    await self.arm()
                elif index_action==2:
                    await self.takeoff()
                elif index_action==3:
                    print("Holding...")
                    self.is_hold=True
                    continue
                elif index_action==4:
                    await self.land()
                else:
                    print("Invaid input")
                print(f"Finish {index_action}!")
            else:
                print("Invalid input!")
                continue
        

if __name__ == "__main__":
    controller = base_controller()
    asyncio.run(controller.run())   