import openai
from openai import OpenAI
import json
import os
import tiktoken
import asyncio
from datetime import datetime

global MAX_ALLOWED_TOKENS, DEEPSEEK_API, BASE_URL, MODEL_NAME
MAX_ALLOWED_TOKENS=4096
DEEPSEEK_API='sk-09099c7f4f704fbd89916c6c7a55a70b'
BASE_URL="https://api.deepseek.com"
MODEL_NAME="deepseek-reasoner"


class Assistant():
    client=None
    response=''
    responses = []
    history=[]
    token_count=0
    enc = tiktoken.encoding_for_model('gpt-4o')

    def __init__(self):
        self.client=OpenAI(
            api_key=DEEPSEEK_API,
            base_url=BASE_URL
        )

    async def answer(self, message):#chat without history
        print(self.get_token_count(message))
        self.response = self.client.chat.completions.create(
            model=MODEL_NAME,
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
        self.get_token_count(message)
        self.history.append({'role':'user', 'content': message})
        self.response = self.client.chat.completions.create(
            model=MODEL_NAME,
            messages=self.history,
            stream=False
        )
        self.history.append({'role':'assistant', 'content': self.response.choices[0].message.content})
        #self.printResponse()
        self.responses.append({'chat': self.response})
    
    def get_token_count(self, text):
        self.token_count=self.token_count+len(self.enc.encode(text))
        return len(self.enc.encode(text))

    def getResponse(self):
        reasoning_content = self.response.choices[0].message.reasoning_content
        content = self.response.choices[0].message.content
        return json.loads(content)

    def printResponse(self):
        reasoning_content = self.response.choices[0].message.reasoning_content
        content = self.response.choices[0].message.content
        print(f"Reasoning: {reasoning_content};")
        print(f"\nResponse: {content}")

if __name__=='__main__':
    ai=Assistant()
    asyncio.run(ai.answer("What is the weather today in Malaysia Selangor"))

