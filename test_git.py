from pathlib import Path
from multi_ai.git.client import GitManager
import shutil
import os

def test():
    print('Testing Git Manager...')
    repo_path = Path('.cache/test_repo')
    
    # Temizlik (Eski testten kalanlari sil)
    if repo_path.exists():
        try:
            def onerror(func, path, exc_info):
                import stat
                if not os.access(path, os.W_OK):
                    os.chmod(path, stat.S_IWUSR)
                    func(path)
                else:
                    raise
            shutil.rmtree(repo_path, onerror=onerror)
        except Exception as e:
            print(f'Warning during cleanup: {e}')

    # 1. Repo Baslat (Init)
    git = GitManager(repo_path)
    
    # --- DUZELTME BASLIYOR ---
    
    # 2. ILK COMMIT (ZORUNLU)
    # Branch acmadan once 'main' dalinda bir seyler olmali.
    (repo_path / 'README.md').write_text('# Test Repo', encoding='utf-8')
    git.commit_all('Initial commit')
    print('✅ Initial commit created (HEAD established)')
    
    # 3. Simdi Branch Acabiliriz
    git.checkout_branch('feature/ai-task-101')
    
    # 4. Ajan Kodunu Yazsin ve Commitlesin
    code_file = repo_path / 'agent_code.py'
    code_file.write_text('print("Committed by AI")', encoding='utf-8')
    git.commit_all('feat: Added AI code')
    
    # --- DUZELTME BITTI ---
    
    print('✅ Git operations successful!')

if __name__ == '__main__':
    test()
