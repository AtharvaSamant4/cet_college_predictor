import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

ROOT_DIR = Path(__file__).resolve().parents[1]
MIGRATIONS_DIR = ROOT_DIR / "database" / "migrations"

def run_migrations():
    load_dotenv(ROOT_DIR / ".env")
    database_url = os.getenv("DATABASE_URL")
    
    if not database_url:
        print("Error: DATABASE_URL not found in .env")
        sys.exit(1)
        
    print("Connecting to database...")
    engine = create_engine(database_url, isolation_level="AUTOCOMMIT")
    
    migration_files = sorted([f for f in os.listdir(MIGRATIONS_DIR) if f.endswith(".sql")])
    
    if not migration_files:
        print("No migration files found.")
        return

    with engine.connect() as conn:
        for file in migration_files:
            file_path = MIGRATIONS_DIR / file
            print(f"Executing migration: {file}...")
            
            with open(file_path, 'r') as f:
                sql_content = f.read()
                
            # Split by statements or just execute whole if engine supports it
            try:
                conn.execute(text(sql_content))
                print(f"Successfully executed {file}")
            except Exception as e:
                print(f"Error executing {file}: {e}")
                sys.exit(1)
                
    print("All migrations completed successfully!")

if __name__ == "__main__":
    run_migrations()
