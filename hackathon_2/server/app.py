from openenv.core.env_server.http_server import create_app
from hackathon_2.models import Hackathon2Action, Hackathon2Observation
from hackathon_2.server.hackathon_2_environment import Hackathon2Environment
import uvicorn
import argparse

# Create the app with web interface and README integration
app = create_app(
    Hackathon2Environment,
    Hackathon2Action,
    Hackathon2Observation,
    env_name="hackathon_2",
    max_concurrent_envs=1,
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", type=str, default="0.0.0.0")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()
    
    uvicorn.run(app, host=args.host, port=args.port)

if __name__ == "__main__":
    main()