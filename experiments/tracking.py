# tracking.py
import os
import dagshub
import mlflow

DAGSHUB_OWNER = "264Gaurav"
DAGSHUB_REPO = "agentic-ai"

def setup_mlflow():
    # Initialize DagsHub <-> MLflow
    dagshub.init(
        repo_owner=DAGSHUB_OWNER,
        repo_name=DAGSHUB_REPO,
        mlflow=True,
    )

    # Optional: set a default experiment for all GenAI runs
    mlflow.set_experiment("genai-agents and agentic-ai")

    # Optional: ensure we log artifacts (JSON traces, etc.)
    os.makedirs("artifacts", exist_ok=True)