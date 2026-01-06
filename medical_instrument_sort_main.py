# Standard Library
import asyncio
import json
import time
import subprocess
import sys

# Third Party
import tkinter as tk
from mavsdk import System
from mavsdk.action import OrbitYawBehavior

# Local Modules
from gui_chat import ChatApp 
from multiple_controller import Multi_controller

class Medical_assistant(ChatApp):
    controller = Multi_controller()

    async def execute_drone_command(self, command):
        intent = command.get("intent").lower().strip()
        print(intent)
        # Perform actions based on intent
        if intent == "search":
            try:
                target = command.get("target")
                direction = command.get("direction")
                distance = command.get("distance_cm")

                self.append_message(sender="System",message=f"   -> Target: {target}")
                self.append_message(sender="System",message=f"   -> Direction: {direction}")
                self.append_message(sender="System",message=f"   -> Distance: {distance} cm")
                if not await self.controller.isArmed():
                    self.append_message(sender="System",message="take off drone")
                    await self.controller.arm()
                    await self.controller.takeoff()
                
                # --- INSERT YOUR ACTUAL DRONE MOVEMENT CODE HERE ---
                # Example: self.drone.move(target, direction, distance)
            except KeyboardInterrupt:
                self.append_message(sender="System",message="action aborted.")

        if intent == "view_camera":
            self.append_message(sender="System",message="Click 'q' or esc to exit")
            self.check_camera()

        elif intent == "recognize_objects":
            target = command.get("target")
            await self.recognize_objects()
            self.append_message(sender="System",message=f"   -> Inspecting object: {target}")

            # --- INSERT YOUR INSPECTION LOGIC HERE ---
            # Example: image = self.drone.camera.capture(target)

        elif intent == "patrol":
            await self.patrol()
            self.append_message(sender="System",message=f"   -> Patrolling: {target}")
 
        elif intent == 'goodbye':
            self.append_message(sender="System",message=f"Landing...")
            await self.controller.land()
            sys.exit()

        elif intent == 'guide':
            None
        else:
            self.append_message(sender="System",message=f"   -> ⚠️ Unknown intent: {intent}")

    async def process_message(self, message):
        """Process message asynchronously and update GUI"""
        try:
            response_data = await self.bot.chat(message)
            # Extract reply and command
            #print(response_data) #for debugging
            reply = response_data.get("reply", "No reply provided.")
            command = response_data.get("command")

            # Log command to console
            if command:
                self.json_output = json.dumps(command, indent=2)
                print(f"[System Log] Command: {self.json_output}")
                await self.execute_drone_command(command)

            # Update GUI in main thread
            self.root.after(0, self.append_message, "Assistant", reply)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.append_message, "System", error_msg)

    def check_camera(self):
        subprocess.Popen(["/usr/bin/python", "/home/yuntian/Drone-workspace/check_camera.py"])

    async def recognize_objects(self):
        time1 = time.time()
        while time.time() - time1 <2:
            await self.controller.manual_control(0,0,0.5,0.6)
            await asyncio.sleep(0.05)
        subprocess.Popen(["/usr/bin/python", "/home/yuntian/Drone-workspace/sub-test-cam.py"])

    async def patrol(self):
        await self.controller.patrol()

if __name__ == "__main__":
    root = tk.Tk()
    app = Medical_assistant(root)

    # Establish connection in async loop
    asyncio.run_coroutine_threadsafe(
        app.controller._establish_connection(), 
        app.loop
    )

    # Handle window close
    def on_closing():
        root.destroy()
        sys.exit()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()

