# Deep Search Agent - Arquivo de configuracao
# Preencha suas chaves de API abaixo

# DeepSeek API Key
DEEPSEEK_API_KEY = "your_deepseek_api_key_here"

# OpenAI API Key (para OpenAI e Codex)
OPENAI_API_KEY = "your_openai_api_key_here"

# Anthropic API Key (para Claude)
ANTHROPIC_API_KEY = "your_anthropic_api_key_here"

# Tavily Search API Key
TAVILY_API_KEY = "your_tavily_api_key_here"

# Provedor LLM: deepseek, openai, ollama, anthropic, codex
DEFAULT_LLM_PROVIDER = "deepseek"

# Modelos por provedor
DEEPSEEK_MODEL = "deepseek-chat"
OPENAI_MODEL = "gpt-4o-mini"
OLLAMA_MODEL = "llama3.1"
OLLAMA_BASE_URL = "http://localhost:11434/v1"
ANTHROPIC_MODEL = "claude-sonnet-4-20250514"
CODEX_MODEL = "o3-mini"

MAX_REFLECTIONS = 2
SEARCH_RESULTS_PER_QUERY = 3
SEARCH_CONTENT_MAX_LENGTH = 20000
OUTPUT_DIR = "reports"
SAVE_INTERMEDIATE_STATES = True
