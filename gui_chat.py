import tkinter as tk
from tkinter import scrolledtext
import datetime
import asyncio
import threading
from Robot_Assistant import Robot_Assistant
import json

class ChatApp:
    json_output = ""

    def __init__(self, root):
        self.root = root
        self.root.title("Medical Drone Assistant")
        self.root.geometry("600x700")

        # Chat display area
        self.chat_display = scrolledtext.ScrolledText(
            root, wrap=tk.WORD, state='disabled', font=("Arial", 12)
        )
        self.chat_display.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self.append_message(
            sender='System',
            message="""═══════════════════════════════════════
🏥 Medical Drone Assistant
Welcome! This software helps you sort medical instruments.
💬 Instructions:
  • Enter natural language commands below
  • Press Enter or click Send to submit
  • Examples: 'Find all scalpels', 'Sort by size'
  • Type 'exit' to quit
═══════════════════════════════════════"""
        )

        # Input area
        self.input_frame = tk.Frame(root)
        self.input_frame.pack(padx=10, pady=10, fill=tk.X)

        self.user_input = tk.Entry(self.input_frame, font=("Arial", 12))
        self.user_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))
        self.user_input.bind("<Return>", self.send_message)

        self.send_button = tk.Button(
            self.input_frame, 
            text="Send", 
            command=self.send_message,
            bg="#4CAF50",
            fg="white",
            font=("Arial", 10, "bold")
        )
        self.send_button.pack(side=tk.RIGHT)

        # Initialize Robot Assistant
        self.bot = Robot_Assistant()

        # Asyncio loop in a separate thread
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self.start_loop, daemon=True)
        self.thread.start()

        # Handle window close properly
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def start_loop(self):
        """Start the asyncio event loop in a separate thread"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def on_close(self):
        """Clean up when window is closed"""
        try:
            self.loop.call_soon_threadsafe(self.loop.stop)
        except:
            pass
        self.root.destroy()

    def send_message(self, event=None):
        """Handle sending user message"""
        message = self.user_input.get()
        if not message.strip():
            return

        # Check for exit command
        if message.lower().strip() in ["exit", "quit", "bye"]:
            self.append_message("You", message)
            self.on_close()
            return

        self.user_input.delete(0, tk.END)
        self.append_message("You", message)

        # Run async task in the separate thread
        asyncio.run_coroutine_threadsafe(self.process_message(message), self.loop)

    async def process_message(self, message):
        """Process message asynchronously and update GUI"""
        try:
            response_data = await self.bot.chat(message)
            # Extract reply and command
            #print(response_data)
            reply = response_data.get("reply", "No reply provided.")
            command = response_data.get("command")

            # Log command to console
            if command:
                self.json_output = json.dumps(command, indent=2)
                print(f"[System Log] Command: {self.json_output}")

            # Update GUI in main thread
            self.root.after(0, self.append_message, "Assistant", reply)

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            self.root.after(0, self.append_message, "System", error_msg)

    def append_message(self, sender, message):
        """Append message to chat display with timestamp"""
        self.chat_display.config(state='normal')

        # Add timestamp
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Format message with sender and timestamp
        formatted_message = f"[{timestamp}] {sender}: {message}\n\n"
        self.chat_display.insert(tk.END, formatted_message)

        # Auto-scroll to bottom
        self.chat_display.see(tk.END)
        self.chat_display.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = ChatApp(root)
    root.mainloop()