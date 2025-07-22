"""Load environment variables from a .env file if it exists, otherwise use system environment variables."""

from dotenv import load_dotenv
from pathlib import Path

def load_env(env_file: str = ".env"):
    dotenv_path = Path(__file__).parent.parent.parent / env_file
    if dotenv_path.exists():
        print(f"Loading environment variables from {dotenv_path}")
        load_dotenv(dotenv_path=dotenv_path, override=True)
    else:
        print(f"⚠️  {dotenv_path} file not found — using environment variables or defaults")

