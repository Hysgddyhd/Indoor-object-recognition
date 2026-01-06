from openai import OpenAI
import json
import asyncio
from AI_Assistant import Assistant

class Robot_Assistant(Assistant):
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
The responses should like in this format:

{
"reply": "<string>", //reponse user message with nartual language, the "reply" is an attribution of one string
"command": {             
    "intent": "<string>",    // search | view_camera | recognize_objects | patrol | goodbye
    "target": "<string>",    // One of the supported instruments or null
    "direction": "<string>", // forward/backward/left/right/up/down or null
    "metadata": { }          // extra task info if needed, e.g. {"degrees": 360}
    }
}

Rules:
1. **Control**:
   - "Take off" -> intent="search"
   - "Rotate/Spin" -> intent="recognize_objects", metadata={"degrees": 360}
   - "Patrol" -> intent="patrol"
2. **Vision**:
   - "Detect objects" -> intent="recognize_objects" (Calls NN model)
   - "Open camera window" -> intent="view_camera" (Opens real-time feed)
3. **Tasks**: "Find X"->search, "Exit"->shutdown.
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
                response_format={'type': 'json_object'},
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

