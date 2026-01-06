import tkinter as tk
from tkinter import scrolledtext
import datetime
import asyncio
import threading
import json
from openai import OpenAI


class Robot_Assistant():
    MAX_ALLOWED_TOKENS = 4096
    BASE_URL = "http://localhost:11434/v1"
    MODEL_NAME = "alibayram/smollm3"
    # Valid target classes for drone navigation
    classes = ['medical beds', 'wheelchairs', 'trolleies', 'anaesthetic machines']

    SYSTEM_PROMPT = """
You are a medical drone assistant.
Goal: Assist staff with instrument management, drone control, and vision tasks.
Supported Instruments: medical beds, wheelchairs, trolleies, anaesthetic machines.

Output JSON ONLY:
{
"reply": "<string>"     
"command": {             //reponse user message with nartual language, the "reply" is an attribution of one string
    "intent": "<string>",    // search | view_camera | recognize objects | shutdown
    "target": "<string>",    // One of the supported instruments or null
    "direction": "<string>", // forward/backward/left/right/up/down or null
    "distance_cm": <number>, // integer or null
    "metadata": { }          // extra task info if needed, e.g. {"degrees": 360}
    }
}

Rules:
1. **Control**:
   - "Take off" -> intent="take_off"
   - "Rotate/Spin" -> intent="rotate", metadata={"degrees": 360}
   - "Patrol" -> intent="patrol"
2. **Vision**:
   - "Detect objects" -> intent="detect_objects" (Calls NN model)
   - "Open camera window" -> intent="view_camera" (Opens real-time feed)
3. **Tasks**: "Find X"->search, "Organize X"->organize, "Status"->check_status.
4. **Fallback**: If unclear, intent="guide". Explain capabilities.
"""

    def __init__(self):
        self.client = OpenAI(
            api_key='ollama',
            base_url=self.BASE_URL
        )
        self.response = None
        self.responses = []
        self.history = []
        self.token_count = 0

    async def answer(self, message) -> dict:
        """
        Process message without history and return structured JSON response
        """
        try:
            self.response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": message},
                ],
                stream=False,
                response_format={'type': 'json_object'}
            )

            # Get response content
            content = self.response.choices[0].message.content

            # Parse JSON
            try:
                answer = json.loads(content)
            except json.JSONDecodeError:
                answer = {
                    "intent": "error",
                    "message": f"Failed to parse JSON from response: {content}"
                }

            self.responses.append({'answer': self.response})
            return answer

        except Exception as e:
            return {
                "intent": "error",
                "message": f"API Error: {str(e)}"
            }

    async def chat(self, message):
        """
        Chat with conversation history
        """
        try:
            # Add user message to history
            self.history.append({'role': 'user', 'content': message})

            # Build messages list with system prompt and history
            messages = [
                {"role": "system", "content": self.SYSTEM_PROMPT}
            ]
            messages.extend(self.history)

            self.response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=messages,
                stream=False,
                response_format={'type': 'json_object'}
            )

            assistant_message = self.response.choices[0].message.content

            # Parse JSON response
            try:
                parsed_response = json.loads(assistant_message)
            except json.JSONDecodeError:
                parsed_response = {
                    "intent": "error",
                    "message": f"Failed to parse JSON from response: {assistant_message}"
                }

            # Add assistant response to history
            self.history.append({'role': 'assistant', 'content': json.dumps(parsed_response)})
            self.responses.append({'chat': self.response})

            return parsed_response

        except Exception as e:
            error_response = {
                "intent": "error",
                "message": f"API Error: {str(e)}"
            }
            self.history.append({'role': 'assistant', 'content': json.dumps(error_response)})
            return error_response

    def get_token_count(self, text):
        """Estimate token count (rough approximation)"""
        estimated_tokens = len(text.split()) * 1.3
        self.token_count += estimated_tokens
        return int(estimated_tokens)

    def printResponse(self):
        """Print the response in a formatted way"""
        if not self.response:
            print("No response available")
            return

        content = self.response.choices[0].message.content
        try:
            parsed = json.loads(content)
            print(json.dumps(parsed, indent=2))
        except json.JSONDecodeError:
            print(content)



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
            print(response_data) #for debugging
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

    def append_message(self, sender='Assistant', message=''):
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