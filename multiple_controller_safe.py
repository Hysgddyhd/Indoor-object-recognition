import asyncio
from aioconsole import ainput
from mavsdk.offboard import OffboardError, VelocityNedYaw, PositionNedYaw
from mavsdk.action import ActionError
import time
import re
import tkinter as tk
from tkinter import scrolledtext
import threading
import json

import curses
#import custom classes
from simple_controller import Simple_controller
from GZModel import Model
from gui_chat import ChatApp

class Multi_controller(Simple_controller, ChatApp):
    
    gz_px4=Model()
    json_output=""
    chatbot = ChatApp
    usage_str = """
        Usage:
        a    print all actions
        c    controller mode
        i    print drone status
        """

    def __init__(self):
        self.root = tk.Tk()
        self.chatbot = ChatApp(self.root)

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



    async def make_user_choose_action(self):
        index_action_str = await ainput("\nWhich action do you want? [0..3] >>> ")
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
        self.root.mainloop()       


if __name__ == "__main__":
    controller = Multi_controller()
    asyncio.run(controller.establish_connection())