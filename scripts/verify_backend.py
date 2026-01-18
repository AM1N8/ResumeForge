import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Define paths
ROOT_DIR = Path(__file__).parent.parent
BACKEND_DIR = ROOT_DIR / "backend"

# Ensure backend is in python path
sys.path.insert(0, str(BACKEND_DIR))

# Load environment variables explicitly
env_path = BACKEND_DIR / ".env"
loaded = load_dotenv(env_path)
print(f"Loaded .env from {env_path}: {loaded}")

# Import app modules
try:
    from app.core.config import get_settings
    from app.core.database import init_db
    from app.services.parsers import ParserFactory
    from app.services.normalization_service import NormalizationService
except ImportError as e:
    print(f"❌ ImportError: {e}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)

async def verify_backend():
    print(">>> Starting Backend Verification...")
    
    # 4. Environment Variables (Check first to fail fast)
    print("\n[1/4] Checking Environment...")
    try:
        settings = get_settings()
        print(f"Database URL: {settings.database_url}")
        print(f"Groq API Key present: {bool(settings.groq_api_key)}")
        
        if settings.groq_api_key:
            print("[OK] Environment loaded correctly")
        else:
            print("[WARN] Groq API Key missing!")
    except Exception as e:
        print(f"[ERR] Environment settings validation failed: {e}")
        return

    # 1. Database Initialization
    print("\n[2/4] Initializing Database...")
    try:
        await init_db()
        print("[OK] Database initialized successfully")
    except Exception as e:
        print(f"[ERR] Database initialization failed: {e}")
        return

    # 2. Parsers
    print("\n[3/4] Testing Parsers...")
    parsers = ParserFactory.get_supported_extensions()
    print(f"Supported extensions: {parsers}")
    if ".pdf" in parsers and ".md" in parsers:
         print("[OK] Parser factory loaded correctly")
    else:
         print("[ERR] Parser factory missing extensions")

    # 3. Normalization
    print("\n[4/4] Testing Normalization...")
    norm = NormalizationService()
    techs = ["react.js", "python3", "JAVA"]
    normalized = norm.normalize_technologies(techs)
    print(f"Normalized {techs} -> {normalized}")
    if "React" in normalized and "Python" in normalized and "Java" in normalized:
        print("[OK] Normalization service working")
    else:
        print("[ERR] Normalization failed")

    print("\n>>> Verification Complete!")

if __name__ == "__main__":
    asyncio.run(verify_backend())
