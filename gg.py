from pathlib import Path
from multi_ai.git.client import GitManager


def test():
    print("Testing Git Manager...")
    # Test için geçici bir klasör
    repo_path = Path(".cache/test_repo")

    git = GitManager(repo_path)

    # 1. Dosya oluştur
    (repo_path / "agent_code.py").write_text("print('Committed by AI')")

    # 2. Branch aç ve commit at
    git.checkout_branch("feature/ai-task-101")
    git.commit_all("feat: Added AI code")

    print("✅ Git operations successful!")


if __name__ == "__main__":
    test()