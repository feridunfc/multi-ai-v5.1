import asyncio
import httpx
import sys
import os

print('=== 🐍 OLLAMA TESTİ BAŞLIYOR ===')
print('Python Version:', sys.version)
print('Current Directory:', os.getcwd())

async def test_ollama():
    print('')
    print('🚀 Ollama API testi başlıyor...')
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            print('📡 API isteği gönderiliyor...')
            response = await client.post(
                'http://127.0.0.1:11434/api/generate',
                json={
                    'model': 'deepseek-coder:6.7b',
                    'prompt': 'Write a Python function to calculate factorial',
                    'stream': False,
                    'options': {'temperature': 0.2}
                }
            )
            print(f'📊 Status Code: {response.status_code}')
            
            if response.status_code == 200:
                data = response.json()
                print('✅ ✅ ✅ BAŞARILI! Ollama çalışıyor!')
                response_text = data.get('response', 'No response')
                print(f'📝 Response: {response_text}')
            else:
                print(f'❌ HTTP Error: {response.text}')
                
    except httpx.ConnectError:
        print('❌ Ollama bağlantı hatası! Ollama çalışıyor mu?')
    except Exception as e:
        print(f'💥 Exception: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    asyncio.run(test_ollama())
    print('')
    print('=== 🏁 TEST TAMAMLANDI ===')
