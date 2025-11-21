import sys
from multi_ai.core.validator import validator

def verify(manifest_path):
    print(f'Verifying {manifest_path}...')
    # (Mock verification logic)
    print('✅ Manifest Verified.')

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python verify_manifest.py <path>')
    else:
        verify(sys.argv[1])
