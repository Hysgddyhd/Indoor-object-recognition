import openai
from openai import OpenAI
import json
import os
import tiktoken
import asyncio
from datetime import datetime
import AI_Assistant

class Robot_Assistant(AI_Assistant.Assistant):
<<<<<<< HEAD
    classes=['scalpel', 'forceps', 'bandage', 'syringe', 'monitor', 'gloves', 'mask', 'scissors', 'thermometer']
    
    SYSTEM_PROMPT = """
        You are an intelligent assistant for a medical instrument organization drone in a hospital.
        Your goal is to assist users (medical staff) in finding, organizing, and inspecting medical instruments.
        
        Your task is to answer user promots quickly, and should avoid deep thinking or check external reference, and return answer as quick as possible.

        Supported Instruments: scalpel, forceps, bandage, syringe, monitor, gloves, mask, scissors, thermometer.

        Your task: Parse human natural-language commands and produce a JSON response.

        You must:
        1. ONLY output valid JSON.
        2. DO NOT output any reasoning or explanations outside the JSON object.
        3. Follow this JSON schema:

        {
        "reply": "<string>",     // Natural language response to the user.
        "command": {             // The command to be executed by the drone, or null if no command is needed
            "intent": "<string>",    // organize | search | inspect | check_status | view_camera | guide | move | stop
            "target": "<string>",    // One of the supported instruments or null
            "direction": "<string>", // forward/backward/left/right/up/down or null
            "distance_cm": <number>, // integer or null
            "metadata": { }          // extra task info if needed
        }
        }

        Handling Rules:
        1. **Guidance (Priority)**: If the user asks for help, is a new user, or provides irrelevant/unclear input (e.g., "hello", "what can you do", "sing a song"), set "intent" to "guide".
           - In the "reply", provide a **detailed** guide. Explain that you can Search, Organize, Inspect, and Report Status. Give specific examples like "Find the scalpel", "Organize bandages", "Show camera", or "Check battery".
        
        2. **Standard Commands**:
           - **Search/Find**: Set "intent" to "search".
           - **Organize**: Set "intent" to "organize".
           - **Status**: Set "intent" to "check_status".
           - **Camera**: Set "intent" to "view_camera".

        3. **Ambiguous/Error**: If the request is not understood or impossible, explain why in "reply" and offer the guidance examples again. Set "intent" to "guide" to help them get back on track.

        4. **Reply Style**: Be professional and helpful. For "guide" intents, the reply can be longer to be informative. For actions, keep it concise.
        """

    def __init__(self):
        super().__init__()
        self.history = [{"role": "system", "content": self.SYSTEM_PROMPT}]

    async def answer(self, message) -> dict:
        print(f"Token count for message: {self.get_token_count(message)}")
        
        # Append user message to history
        self.history.append({"role": "user", "content": message})
        
        # Limit history to prevent token overflow (simple sliding window)
        if len(self.history) > 10:
             # Keep system prompt and last 8 messages
            self.history = [self.history[0]] + self.history[-9:]

        self.response = self.client.chat.completions.create(
            model=AI_Assistant.MODEL_NAME,
            messages=self.history,
=======
    classes=['bed', 'bookshelf', 'chair', 'closet', 'door', 'fridge', 'sofa', 'table', 'trashBin']
    SYSTEM_PROMPT = """
        You are an LLM for a drone indoor navigation system.
        Your task: Parse human natural-language commands and produce a JSON command
        that will be executed by the drone’s local controller.

        You must:
        1. ONLY output valid JSON, no explanations.
        2. Follow this JSON schema:

        {
        "intent": "<string>",    // move | search | inspect | report
        "target": "<string>",    // one of: bed, bookshelf, chair, closet, door, fridge, sofa, table, trashBin or null
        "direction": "<string>", // forward/backward/left/right/up/down or null
        "distance_cm": <number>, // integer or null
        "metadata": { }          // extra task info if needed
        }

        3. If user request is ambiguous or impossible, return:
        {
        "intent": "error",
        "message": "<error_reason>"
        }

        4. NEVER output text outside JSON.
        """
    async def answer(self, message) -> dict:#chat without history
        print(self.get_token_count(message))
        self.response = self.client.chat.completions.create(
            model=AI_Assistant.MODEL_NAME,
            messages=[
                {"role": "system",
                 "content": self.SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": message
                },
            ],
>>>>>>> 6b3d3f6b5d8a5ad1120d6a6d362fb16fccbee894
            stream=False,
            response_format={
                'type': 'json_object'
            }
        )
        
<<<<<<< HEAD
        # Append assistant response to history
        assistant_content = self.response.choices[0].message.content
        self.history.append({"role": "assistant", "content": assistant_content})

        answer = self.getResponse()
        self.responses.append({'answer': self.response})
        return answer

    def printResponse(self):
        """
        Overrides the base class printResponse to parse and display the JSON output user-friendly.
        """
        try:
            # Not showing reasoning content to the user as requested
            # reasoning_content = self.response.choices[0].message.reasoning_content
            content_str = self.response.choices[0].message.content
            
            try:
                data = json.loads(content_str)
                reply = data.get("reply", "No reply provided.")
                command = data.get("command")
                
                print(f"Assistant: {reply}")
                if command:
                    print(f"Command (System Only): {command.get('intent')} -> {command.get('target') or 'N/A'}")
                    print(f"Full Command: {json.dumps(command, indent=2)}")
            except json.JSONDecodeError:
                print(f"Response (Raw): {content_str}")
                
        except Exception as e:
            print(f"Error printing response: {e}")
            # Fallback to parent method if structure is different
            super().printResponse()

=======
        answer = self.getResponse()
        self.responses.append({'answer': self.response})
        return answer
>>>>>>> 6b3d3f6b5d8a5ad1120d6a6d362fb16fccbee894
        

if __name__=='__main__':
    bot=Robot_Assistant()
    answer = asyncio.run(bot.answer("Who won the world series in 2020? Please respond in the json format {winner: ...}"))
    print(answer)