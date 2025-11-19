from multi_ai.sandbox.filesystem import SandboxFileSystem
import shutil

def test():
    print('🛡️  Testing Security Sandbox...')
    fs = SandboxFileSystem(task_id='test-task-001')
    
    # 1. Dosya Yazma Testi
    file_path = fs.write_file('main.py', 'print("Hello AI World")')
    print(f'✅ File Written: {file_path}')
    
    # 2. Okuma Testi
    content = fs.read_file('main.py')
    assert content == 'print("Hello AI World")'
    print('✅ File Read Verified')
    
    # 3. Güvenlik Testi (Hack Denemesi)
    try:
        fs.write_file('../hack_system.txt', 'ATTACK')
        print('❌ Security FAILED! Sandbox escaped.')
    except PermissionError:
        print('✅ Security PASSED: Path traversal blocked.')

    # Temizlik
    fs.clean()

if __name__ == '__main__':
    test()
