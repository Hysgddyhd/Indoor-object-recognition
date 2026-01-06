from openai import OpenAI
import json
import asyncio



class Assistant():
    # Configuration
    MAX_ALLOWED_TOKENS = 4096
    BASE_URL = "http://localhost:11434/v1"
    MODEL_NAME = "alibayram/smollm3"
    def __init__(self):
        self.client = OpenAI(
            api_key='ollama',
            base_url=self.BASE_URL
        )
        self.response = None
        self.responses = []
        self.history = []
        self.token_count = 0

    async def answer(self, message):
        """Chat without history"""
        print(f"Token count: {self.get_token_count(message)}")

        self.response = self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=[
                {
                    "role": "user",
                    "content": message
                },
            ],
            stream=False
        )

        self.printResponse()
        self.responses.append({'answer': self.response})

    async def chat(self, message):
        """Chat with history"""
        self.get_token_count(message)
        self.history.append({'role': 'user', 'content': message})

        self.response = self.client.chat.completions.create(
            model=self.MODEL_NAME,
            messages=self.history,
            stream=False
        )

        assistant_message = self.response.choices[0].message.content
        self.history.append({'role': 'assistant', 'content': assistant_message})
        self.responses.append({'chat': self.response})

        return assistant_message

    def get_token_count(self, text):
        """Estimate token count (rough approximation)"""
        # SmolLM3 uses different tokenizer, this is approximate
        # For accurate counting, use Ollama's API or model-specific tokenizer
        estimated_tokens = len(text.split()) * 1.3  # Rough estimate
        self.token_count += estimated_tokens
        return int(estimated_tokens)

    def getResponse(self):
        """Get response content, optionally parse as JSON"""
        content = self.response.choices[0].message.content

        try:
            # Try to parse as JSON if content looks like JSON
            if content.strip().startswith('{') or content.strip().startswith('['):
                return json.loads(content)
            return content
        except json.JSONDecodeError:
            return content

    def printResponse(self):
        """Print the response"""
        content = self.response.choices[0].message.content
        print(f"Response: {content}")

if __name__ == '__main__':
    ai = Assistant()
    asyncio.run(ai.answer("What is the weather today in Malaysia Selangor"))
