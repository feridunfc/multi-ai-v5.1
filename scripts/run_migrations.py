import os
import sqlite3

MIGRATIONS_DIR = 'migrations'
DB_PATH = '.cache/ledger.db'

def main():
    print(f'Running migrations on {DB_PATH}...')
    # (Mock migration logic)
    print('✅ Migrations applied.')

if __name__ == '__main__':
    main()
