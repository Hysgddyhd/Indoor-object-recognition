from openai import OpenAI
import json
import asyncio
from AI_Assistant import Assistant

class Robot_Assistant(Assistant):
    # Valid target classes for drone navigation
    classes = ['bed', 'bookshelf', 'chair', 'closet', 'door', 'fridge', 'sofa', 'table', 'trashBin']

    SYSTEM_PROMPT = """
You are an intelligent assistant for a medical instrument organization drone in a hospital.
Your goal is to assist users (medical staff) in finding, organizing, and inspecting medical instruments.

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

    async def answer(self, message) -> dict:
        """
        Process message without history and return structured JSON response
        """
        try:
            self.response = self.client.chat.completions.create(
                model=self.Mo,
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

