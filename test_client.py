import asyncio
import sys
import os

print('=== 🔧 ROBUST OLLAMA CLIENT TESTİ ===')

# Tüm olası yolları dene
possible_paths = [
    os.path.join(os.getcwd(), 'libs', 'utils', 'src'),
    os.path.join(os.getcwd(), 'libs', 'utils', 'src', 'multi_ai'),
    os.path.join(os.getcwd()),
    os.path.join(os.getcwd(), 'libs'),
]

for path in possible_paths:
    if os.path.exists(path) and path not in sys.path:
        sys.path.insert(0, path)
        print(f'✅ Yol eklendi: {path}')

print('')
print('📂 Mevcut dosya yapısı:')
utils_src_path = os.path.join(os.getcwd(), 'libs', 'utils', 'src')
if os.path.exists(utils_src_path):
    for root, dirs, files in os.walk(utils_src_path):
        level = root.replace(utils_src_path, '').count(os.sep)
        indent = ' ' * 2 * level
        print(f'{indent}📁 {os.path.basename(root)}/')
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            if file.endswith('.py'):
                print(f'{subindent}📄 {file}')
else:
    print('❌ libs/utils/src bulunamadı!')

print('')
print('🔄 Import denemesi...')
try:
    from multi_ai.utils.robust_ollama_client import RobustOllamaClient
    print('✅ ✅ ✅ RobustOllamaClient başarıyla import edildi!')
    
    # Client testi
    async def test_client():
        print('')
        print('🚀 Client testi başlıyor...')
        client = RobustOllamaClient()
        result = await client.generate(
            model='deepseek-coder:6.7b',
            prompt='Write hello world in Python',
            options={'temperature': 0.2}
        )
        print('✅ ✅ ✅ CLIENT BAŞARILI!')
        response_text = result.get('response', 'No response')
        print(f'Response: {response_text}')
    
    asyncio.run(test_client())
    
except ImportError as e:
    print(f'❌ Import hatası: {e}')
    print('')
    print('🔍 PYTHONPATH:')
    for p in sys.path:
        print(f'  {p}')

print('')
print('=== 🏁 CLIENT TEST TAMAMLANDI ===')
