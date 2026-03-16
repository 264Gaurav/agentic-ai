from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import time
import mlflow

load_dotenv()


def get_gemini_llm(model: str = "gemini-2.5-flash"):
    """
    Get a Gemini LLM instance.
    
    Args:
        model: Name of the Gemini model to use. Defaults to "gemini-2.5-flash"
    
    Returns:
        ChatGoogleGenerativeAI instance configured with the specified model
    """
    return ChatGoogleGenerativeAI(model=model)


class TracedLLM:
    """
    Lightweight wrapper that logs per-call latency and model metadata to MLflow.
    Compatible with LangChain's Runnable interface (delegates everything to the
    underlying LLM except for `invoke`).
    """

    def __init__(self, llm: ChatGoogleGenerativeAI, name: str = "gemini"):
        self._llm = llm
        self._name = name

    def invoke(self, input, config=None, **kwargs):
        start = time.time()
        result = self._llm.invoke(input, config=config, **kwargs)
        duration = time.time() - start

        # Per-call metrics
        mlflow.log_metric(f"{self._name}_latency_s", duration)
        mlflow.log_param(f"{self._name}_model", getattr(self._llm, "model", "unknown"))

        return result

    def __getattr__(self, item):
        # Delegate all other attributes/methods (e.g. bind_tools, with_config, etc.)
        return getattr(self._llm, item)


# Default instance for easy import, with per-call tracing enabled
default_gemini_llm = TracedLLM(get_gemini_llm())
