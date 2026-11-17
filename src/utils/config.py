"""
配置管理模块
处理环境变量和配置参数
"""

import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class Config:
    """配置类"""
    # API密钥
    deepseek_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    tavily_api_key: Optional[str] = None

    # 模型配置
    default_llm_provider: str = "deepseek"  # deepseek, openai, ollama, anthropic, codex
    deepseek_model: str = "deepseek-chat"
    openai_model: str = "gpt-4o-mini"
    ollama_model: str = "llama3.1"
    ollama_base_url: str = "http://localhost:11434/v1"
    anthropic_model: str = "claude-sonnet-4-20250514"
    codex_model: str = "o3-mini"
    
    # 搜索配置
    max_search_results: int = 3
    search_timeout: int = 240
    max_content_length: int = 20000
    
    # Agent配置
    max_reflections: int = 2
    max_paragraphs: int = 5
    
    # 输出配置
    output_dir: str = "reports"
    save_intermediate_states: bool = True
    
    def validate(self) -> bool:
        """验证配置"""
        # 检查必需的API密钥
        if self.default_llm_provider == "deepseek" and not self.deepseek_api_key:
            print("Erro: DeepSeek API Key nao definida")
            return False

        if self.default_llm_provider == "openai" and not self.openai_api_key:
            print("Erro: OpenAI API Key nao definida")
            return False

        if self.default_llm_provider == "anthropic" and not self.anthropic_api_key:
            print("Erro: Anthropic API Key nao definida")
            return False

        if self.default_llm_provider == "codex" and not self.openai_api_key:
            print("Erro: OpenAI API Key nao definida (necessaria para Codex)")
            return False

        # Ollama nao precisa de API key

        if not self.tavily_api_key:
            print("Erro: Tavily API Key nao definida")
            return False

        return True
    
    @classmethod
    def from_file(cls, config_file: str) -> "Config":
        """从配置文件创建配置"""
        if config_file.endswith('.py'):
            # Python配置文件
            import importlib.util
            
            # 动态导入配置文件
            spec = importlib.util.spec_from_file_location("config", config_file)
            config_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(config_module)
            
            return cls(
                deepseek_api_key=getattr(config_module, "DEEPSEEK_API_KEY", None),
                openai_api_key=getattr(config_module, "OPENAI_API_KEY", None),
                anthropic_api_key=getattr(config_module, "ANTHROPIC_API_KEY", None),
                tavily_api_key=getattr(config_module, "TAVILY_API_KEY", None),
                default_llm_provider=getattr(config_module, "DEFAULT_LLM_PROVIDER", "deepseek"),
                deepseek_model=getattr(config_module, "DEEPSEEK_MODEL", "deepseek-chat"),
                openai_model=getattr(config_module, "OPENAI_MODEL", "gpt-4o-mini"),
                ollama_model=getattr(config_module, "OLLAMA_MODEL", "llama3.1"),
                ollama_base_url=getattr(config_module, "OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                anthropic_model=getattr(config_module, "ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                codex_model=getattr(config_module, "CODEX_MODEL", "o3-mini"),
                max_search_results=getattr(config_module, "SEARCH_RESULTS_PER_QUERY", 3),
                search_timeout=getattr(config_module, "SEARCH_TIMEOUT", 240),
                max_content_length=getattr(config_module, "SEARCH_CONTENT_MAX_LENGTH", 20000),
                max_reflections=getattr(config_module, "MAX_REFLECTIONS", 2),
                max_paragraphs=getattr(config_module, "MAX_PARAGRAPHS", 5),
                output_dir=getattr(config_module, "OUTPUT_DIR", "reports"),
                save_intermediate_states=getattr(config_module, "SAVE_INTERMEDIATE_STATES", True)
            )
        else:
            # .env格式配置文件
            config_dict = {}
            
            if os.path.exists(config_file):
                with open(config_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            config_dict[key.strip()] = value.strip()
            
            return cls(
                deepseek_api_key=config_dict.get("DEEPSEEK_API_KEY"),
                openai_api_key=config_dict.get("OPENAI_API_KEY"),
                anthropic_api_key=config_dict.get("ANTHROPIC_API_KEY"),
                tavily_api_key=config_dict.get("TAVILY_API_KEY"),
                default_llm_provider=config_dict.get("DEFAULT_LLM_PROVIDER", "deepseek"),
                deepseek_model=config_dict.get("DEEPSEEK_MODEL", "deepseek-chat"),
                openai_model=config_dict.get("OPENAI_MODEL", "gpt-4o-mini"),
                ollama_model=config_dict.get("OLLAMA_MODEL", "llama3.1"),
                ollama_base_url=config_dict.get("OLLAMA_BASE_URL", "http://localhost:11434/v1"),
                anthropic_model=config_dict.get("ANTHROPIC_MODEL", "claude-sonnet-4-20250514"),
                codex_model=config_dict.get("CODEX_MODEL", "o3-mini"),
                max_search_results=int(config_dict.get("SEARCH_RESULTS_PER_QUERY", "3")),
                search_timeout=int(config_dict.get("SEARCH_TIMEOUT", "240")),
                max_content_length=int(config_dict.get("SEARCH_CONTENT_MAX_LENGTH", "20000")),
                max_reflections=int(config_dict.get("MAX_REFLECTIONS", "2")),
                max_paragraphs=int(config_dict.get("MAX_PARAGRAPHS", "5")),
                output_dir=config_dict.get("OUTPUT_DIR", "reports"),
                save_intermediate_states=config_dict.get("SAVE_INTERMEDIATE_STATES", "true").lower() == "true"
            )


def load_config(config_file: Optional[str] = None) -> Config:
    """
    加载配置
    
    Args:
        config_file: 配置文件路径，如果不指定则使用默认路径
        
    Returns:
        配置对象
    """
    # 确定配置文件路径
    if config_file:
        if not os.path.exists(config_file):
            raise FileNotFoundError(f"配置文件不存在: {config_file}")
        file_to_load = config_file
    else:
        # 尝试加载常见的配置文件
        for config_path in ["config.py", "config.env", ".env"]:
            if os.path.exists(config_path):
                file_to_load = config_path
                print(f"已找到配置文件: {config_path}")
                break
        else:
            raise FileNotFoundError("未找到配置文件，请创建 config.py 文件")
    
    # 创建配置对象
    config = Config.from_file(file_to_load)
    
    # 验证配置
    if not config.validate():
        raise ValueError("配置验证失败，请检查配置文件中的API密钥")
    
    return config


def print_config(config: Config):
    """打印配置信息（隐藏敏感信息）"""
    print("\n=== 当前配置 ===")
    print(f"Provedor LLM: {config.default_llm_provider}")
    print(f"DeepSeek modelo: {config.deepseek_model}")
    print(f"OpenAI modelo: {config.openai_model}")
    print(f"Ollama modelo: {config.ollama_model}")
    print(f"Anthropic modelo: {config.anthropic_model}")
    print(f"Codex modelo: {config.codex_model}")
    print(f"Max resultados busca: {config.max_search_results}")
    print(f"Timeout busca: {config.search_timeout}s")
    print(f"Max tamanho conteudo: {config.max_content_length}")
    print(f"Max reflexoes: {config.max_reflections}")
    print(f"Max paragrafos: {config.max_paragraphs}")
    print(f"Diretorio saida: {config.output_dir}")
    print(f"Salvar estados intermediarios: {config.save_intermediate_states}")

    # Status das API Keys
    print(f"DeepSeek API Key: {'definida' if config.deepseek_api_key else 'nao definida'}")
    print(f"OpenAI API Key: {'definida' if config.openai_api_key else 'nao definida'}")
    print(f"Anthropic API Key: {'definida' if config.anthropic_api_key else 'nao definida'}")
    print(f"Tavily API Key: {'definida' if config.tavily_api_key else 'nao definida'}")
    print("==================\n")
