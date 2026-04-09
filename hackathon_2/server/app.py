import sys
import os
import argparse
import uvicorn

# Add the repo root to Python path so 'models' can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from openenv.core.env_server.http_server import create_app
from models import Hackathon2Action, Hackathon2Observation
from server.hackathon_2_environment import Hackathon2Environment

# Create the app with web interface and README integration
app = create_app(
    Hackathon2Environment,
    Hackathon2Action,
    Hackathon2Observation,
    env_name="hackathon_2",
    max_concurrent_envs=1,
)

# -----------------------------
# Health check endpoint
# -----------------------------
@app.get("/")
def health_check():
    return {"status": "ok"}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", 7860)))  # HF-friendly port
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()
