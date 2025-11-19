import asyncio
from multi_ai.llm.client import llm_client

async def main():
    print('🧠 Connecting to Ollama (Llama 3.2)...')
    
    prompt = 'Write a very short python function that adds two numbers.'
    
    try:
        response = await llm_client.generate(
            prompt=prompt,
            system_prompt='You are an expert Python coder. Be concise.'
        )
        print('\n🤖 AI Response:\n')
        print(response)
    except Exception as e:
        print(f'❌ Failed: {e}')

if __name__ == '__main__':
    asyncio.run(main())
