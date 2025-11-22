import os
import sys

print('=== 🗺️  YOL TESTİ BAŞLIYOR ===')

# Temporal runner'ın gerçek yolu
current_file = r'C:\Users\user\PycharmProjects\MULTI_AI_v51\apps\review_worker\src\multi_ai\review_worker\temporal_runner.py'
print('📄 Mevcut dosya:', current_file)
print('')

# Farklı seviyelerdeki yolları test et
print('🔍 Seviye seviye yukarı çıkılıyor:')
temp_path = current_file

for i in range(8):  # 8 seviye yukarı çık
    temp_path = os.path.dirname(temp_path)
    has_multi_ai = 'MULTI_AI_v51' in temp_path
    has_apps = 'apps' in temp_path
    has_review = 'review_worker' in temp_path
    
    status = '✅ DOĞRU KÖK' if has_multi_ai and not has_apps and not has_review else '➡️  DEVAM'
    
    print(f'  {i+1}. {temp_path}')
    print(f'      📍 Durum: {status}')
    
    if has_multi_ai and not has_apps and not has_review:
        print(f'')
        print(f'🎯 ✅ DOĞRU PROJE KÖKÜ BULUNDU: {temp_path}')
        break
    elif i == 7:
        print(f'')
        print('❌ Proje kökü bulunamadı! Son yol:', temp_path)

print('')
print('=== 🏁 YOL TESTİ TAMAMLANDI ===')
