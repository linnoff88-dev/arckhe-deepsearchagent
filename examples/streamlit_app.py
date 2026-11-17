"""
Interface Web com Streamlit
Interface amigavel para o DeepSearchAgent
"""

import os
import sys
import streamlit as st
from datetime import datetime
import json

# Adicionar diretorio src ao path do Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import DeepSearchAgent, Config


def main():
    """Funcao principal"""
    st.set_page_config(
        page_title="DeepSearchAgent",
        page_icon="🔍",
        layout="wide"
    )

    st.title("DeepSearchAgent")
    st.markdown("Agente de pesquisa profunda com IA — sem dependencia de frameworks")

    # Sidebar de configuracao
    with st.sidebar:
        st.header("Configuracao")

        # Selecao de provedor
        st.subheader("Provedor de LLM")
        llm_provider = st.selectbox(
            "Provedor",
            ["deepseek", "openai", "ollama", "anthropic", "codex"],
            help="Escolha o provedor de LLM"
        )

        # Chaves de API dinamicas por provedor
        st.subheader("Chaves de API")
        tavily_key = st.text_input("Tavily API Key", type="password", value="")

        deepseek_key = ""
        openai_key = ""
        anthropic_key = ""
        ollama_base_url = "http://localhost:11434/v1"

        if llm_provider == "deepseek":
            deepseek_key = st.text_input("DeepSeek API Key", type="password", value="")
            model_name = st.selectbox("Modelo DeepSeek", ["deepseek-chat"])

        elif llm_provider == "openai":
            openai_key = st.text_input("OpenAI API Key", type="password", value="")
            model_name = st.selectbox("Modelo OpenAI", ["gpt-4o-mini", "gpt-4o"])

        elif llm_provider == "ollama":
            ollama_base_url = st.text_input("Ollama URL", value="http://localhost:11434/v1")
            model_name = st.text_input("Modelo Ollama", value="llama3.1",
                                       help="Ex: llama3.1, mistral, codellama, deepseek-r1")

        elif llm_provider == "anthropic":
            anthropic_key = st.text_input("Anthropic API Key", type="password", value="")
            model_name = st.selectbox("Modelo Claude", [
                "claude-sonnet-4-20250514",
                "claude-haiku-4-5-20251001",
                "claude-opus-4-20250514"
            ])

        elif llm_provider == "codex":
            openai_key = st.text_input("OpenAI API Key", type="password", value="")
            model_name = st.selectbox("Modelo Codex", ["o3-mini", "o4-mini", "gpt-4o"])

        # Configuracoes avancadas
        st.subheader("Configuracoes avancadas")
        max_reflections = st.slider("Rodadas de reflexao", 1, 5, 2)
        max_search_results = st.slider("Resultados por busca", 1, 10, 3)
        max_content_length = st.number_input("Tamanho maximo do conteudo", 1000, 50000, 20000)

    # Interface principal
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("Consulta de pesquisa")
        query = st.text_area(
            "Digite o tema que deseja pesquisar",
            placeholder="Ex.: Tendencias de inteligencia artificial em 2025",
            height=100
        )

        # Exemplos de consulta
        st.subheader("Exemplos de consulta")
        example_queries = [
            "Tendencias de inteligencia artificial em 2025",
            "Aplicacoes de deep learning na area da saude",
            "Ultimos avancos em tecnologia blockchain",
            "Tendencias em energia sustentavel",
            "Estado atual da computacao quantica"
        ]

        selected_example = st.selectbox("Selecionar exemplo", ["Personalizada"] + example_queries)
        if selected_example != "Personalizada":
            query = selected_example

    with col2:
        st.header("Status")
        if 'agent' in st.session_state and hasattr(st.session_state.agent, 'state'):
            progress = st.session_state.agent.get_progress_summary()
            st.metric("Total de paragrafos", progress['total_paragraphs'])
            st.metric("Concluidos", progress['completed_paragraphs'])
            st.progress(progress['progress_percentage'] / 100)
        else:
            st.info("Nenhuma pesquisa em andamento")

    # Botao de execucao
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        start_research = st.button("Iniciar pesquisa", type="primary", use_container_width=True)

    # Validacao de configuracao
    if start_research:
        if not query.strip():
            st.error("Por favor, insira um tema de pesquisa")
            return

        if not tavily_key:
            st.error("Por favor, insira a Tavily API Key")
            return

        if llm_provider == "deepseek" and not deepseek_key:
            st.error("Por favor, insira a DeepSeek API Key")
            return

        if llm_provider == "openai" and not openai_key:
            st.error("Por favor, insira a OpenAI API Key")
            return

        if llm_provider == "anthropic" and not anthropic_key:
            st.error("Por favor, insira a Anthropic API Key")
            return

        if llm_provider == "codex" and not openai_key:
            st.error("Por favor, insira a OpenAI API Key (necessaria para Codex)")
            return

        # Criar configuracao
        config = Config(
            deepseek_api_key=deepseek_key or None,
            openai_api_key=openai_key or None,
            anthropic_api_key=anthropic_key or None,
            tavily_api_key=tavily_key,
            default_llm_provider=llm_provider,
            deepseek_model=model_name if llm_provider == "deepseek" else "deepseek-chat",
            openai_model=model_name if llm_provider == "openai" else "gpt-4o-mini",
            ollama_model=model_name if llm_provider == "ollama" else "llama3.1",
            ollama_base_url=ollama_base_url if llm_provider == "ollama" else "http://localhost:11434/v1",
            anthropic_model=model_name if llm_provider == "anthropic" else "claude-sonnet-4-20250514",
            codex_model=model_name if llm_provider == "codex" else "o3-mini",
            max_reflections=max_reflections,
            max_search_results=max_search_results,
            max_content_length=max_content_length,
            output_dir="streamlit_reports"
        )

        # Executar pesquisa
        execute_research(query, config)


def execute_research(query: str, config: Config):
    """Executa a pesquisa"""
    try:
        # Criar barra de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()

        # Inicializar o agente
        status_text.text("Inicializando o agente...")
        agent = DeepSearchAgent(config)
        st.session_state.agent = agent

        progress_bar.progress(10)

        # Gerar estrutura do relatorio
        status_text.text("Gerando estrutura do relatorio...")
        agent._generate_report_structure(query)
        progress_bar.progress(20)

        # Processar paragrafos
        total_paragraphs = len(agent.state.paragraphs)
        for i in range(total_paragraphs):
            status_text.text(f"Processando paragrafo {i+1}/{total_paragraphs}: {agent.state.paragraphs[i].title}")

            # Busca inicial e resumo
            agent._initial_search_and_summary(i)
            progress_value = 20 + (i + 0.5) / total_paragraphs * 60
            progress_bar.progress(int(progress_value))

            # Loop de reflexao
            agent._reflection_loop(i)
            agent.state.paragraphs[i].research.mark_completed()

            progress_value = 20 + (i + 1) / total_paragraphs * 60
            progress_bar.progress(int(progress_value))

        # Gerar relatorio final
        status_text.text("Gerando relatorio final...")
        final_report = agent._generate_final_report()
        progress_bar.progress(90)

        # Salvar relatorio
        status_text.text("Salvando relatorio...")
        agent._save_report(final_report)
        progress_bar.progress(100)

        status_text.text("Pesquisa concluida!")

        # Exibir resultados
        display_results(agent, final_report)

    except Exception as e:
        st.error(f"Erro durante a pesquisa: {str(e)}")


def display_results(agent: DeepSearchAgent, final_report: str):
    """Exibe os resultados da pesquisa"""
    st.header("Resultados da pesquisa")

    # Abas de resultado
    tab1, tab2, tab3 = st.tabs(["Relatorio final", "Detalhes", "Download"])

    with tab1:
        st.markdown(final_report)

    with tab2:
        # Detalhes dos paragrafos
        st.subheader("Detalhes dos paragrafos")
        for i, paragraph in enumerate(agent.state.paragraphs):
            with st.expander(f"Paragrafo {i+1}: {paragraph.title}"):
                st.write("**Conteudo previsto:**", paragraph.content)
                st.write("**Conteudo final:**", paragraph.research.latest_summary[:300] + "..."
                        if len(paragraph.research.latest_summary) > 300
                        else paragraph.research.latest_summary)
                st.write("**Buscas realizadas:**", paragraph.research.get_search_count())
                st.write("**Rodadas de reflexao:**", paragraph.research.reflection_iteration)

        # Historico de buscas
        st.subheader("Historico de buscas")
        all_searches = []
        for paragraph in agent.state.paragraphs:
            all_searches.extend(paragraph.research.search_history)

        if all_searches:
            for i, search in enumerate(all_searches):
                with st.expander(f"Busca {i+1}: {search.query}"):
                    st.write("**URL:**", search.url)
                    st.write("**Titulo:**", search.title)
                    st.write("**Previa do conteudo:**", search.content[:200] + "..." if len(search.content) > 200 else search.content)
                    if search.score:
                        st.write("**Pontuacao de relevancia:**", search.score)

    with tab3:
        # Opcoes de download
        st.subheader("Baixar relatorio")

        # Download em Markdown
        st.download_button(
            label="Baixar relatorio em Markdown",
            data=final_report,
            file_name=f"relatorio_pesquisa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown"
        )

        # Download do estado em JSON
        state_json = agent.state.to_json()
        st.download_button(
            label="Baixar arquivo de estado",
            data=state_json,
            file_name=f"estado_pesquisa_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json"
        )


if __name__ == "__main__":
    main()
