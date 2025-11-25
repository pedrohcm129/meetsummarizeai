import base64
import os
from typing import Optional

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types
from streamlit_js_eval import streamlit_js_eval


# =========================================
# Helpers para base64 / localStorage
# =========================================

def encode_b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("utf-8")


def decode_b64(text: Optional[str]) -> Optional[str]:
    if not text:
        return None
    try:
        return base64.b64decode(text.encode("utf-8")).decode("utf-8")
    except Exception:
        return None


# =========================================
# Config inicial
# =========================================

load_dotenv()

st.set_page_config(
    page_title="MeetSummarizeAI · Gemini",
    page_icon="🎙️",
    layout="centered",
)

st.markdown(
    """
    <h1 style='text-align:center;'>🎙️ MeetSummarizeAI</h1>
    <p style='text-align:center; font-size:18px; color:#666;'>Transcreva e resuma reuniões com um clique.</p>
    """,
    unsafe_allow_html=True,
)


LOCALSTORAGE_KEY = "MT_GEMINI_API_KEY_B64"


# =========================================
# Seção: API Key (container estilizado)
# =========================================

with st.container(border=True):
    st.markdown("### 🔑 Configuração da API Key do Gemini")
    st.write("Salve sua chave localmente para não digitar toda vez.")

    saved_key_b64 = streamlit_js_eval(
        js_expressions=f"localStorage.getItem('{LOCALSTORAGE_KEY}')",
        key="mt_get_gemini_key",
    )
    saved_key = decode_b64(saved_key_b64)

    if "gemini_api_key" not in st.session_state:
        st.session_state.gemini_api_key = saved_key or os.getenv("GEMINI_API_KEY", "")

    api_key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state.gemini_api_key,
        type="password",
    )

    col1, col2, col3 = st.columns(3)

    # --- Botão para carregar a key do navegador ---
    with col1:
        if st.button("🔍 Carregar do navegador"):
            loaded_b64 = streamlit_js_eval(
                js_expressions=f"localStorage.getItem('{LOCALSTORAGE_KEY}')",
                key="mt_load_key_button",
            )
            loaded_key = decode_b64(loaded_b64)

            if loaded_key:
                st.session_state.gemini_api_key = loaded_key
                st.success("Chave carregada do navegador!")
            else:
                st.warning("Nenhuma chave encontrada no navegador.")

    # --- Botão para salvar a key no navegador ---
    with col2:
        if st.button("💾 Salvar no navegador"):
            if not api_key_input:
                st.warning("Informe uma chave antes de salvar.")
            else:
                encoded = encode_b64(api_key_input)
                streamlit_js_eval(
                    js_expressions=(
                        f"localStorage.setItem('{LOCALSTORAGE_KEY}', '{encoded}')"
                    ),
                    key="mt_set_gemini_key",
                )
                st.session_state.gemini_api_key = api_key_input
                st.success("Chave salva no navegador!")

    # --- Botão para limpar a key do navegador ---
    with col3:
        if st.button("🗑️ Limpar chave salva"):
            streamlit_js_eval(
                js_expressions=f"localStorage.removeItem('{LOCALSTORAGE_KEY}')",
                key="mt_clear_gemini_key",
            )
            st.session_state.gemini_api_key = ""
            st.success("Chave removida do navegador!")

    API_KEY = api_key_input or os.getenv("GEMINI_API_KEY")

    if not API_KEY:
        st.error("Nenhuma API key encontrada.")
        st.stop()


# =========================================
# Cliente Gemini
# =========================================

MODEL_NAME = "gemini-2.5-flash"
client = genai.Client(api_key=API_KEY)


# =========================================
# Função principal de transcrição/resumo
# =========================================

def transcrever_audio_bytes(audio_bytes: bytes, mime_type: str, modo: str) -> str:

    if modo == "transcricao":
        prompt = (
            "Transcreva o áudio enviado em português, mantendo a estrutura de falas "
            "de forma clara."
        )
    else:
        prompt = (
            "Você recebeu o áudio de uma reunião. "
            """### Instrução ###

Você é um assistente experiente em reuniões corporativas.  
Sua tarefa é analisar a transcrição da reunião fornecida e criar uma ata estruturada.

### Objetivo ###

A ata deve conter os seguintes elementos:

1. **Resumo geral da reunião**  
   Um parágrafo introdutório com os temas centrais abordados.

2. **Principais pontos discutidos**  
   Listados de forma clara e objetiva.

3. **Tarefas identificadas**  
   Apresente cada tarefa no seguinte formato:

   | Nome da Tarefa | Responsável         | Prazo           | Ações para realizar a tarefa                          |
   |----------------|----------------------|------------------|--------------------------------------------------------|
   | [Título claro] | [Nome ou "Não especificado"] | [Data ou "Não especificado"] | - [Passo 1] <br> - [Passo 2] <br> - [Passo 3] ... |

4. **Decisões tomadas**  
   Liste acordos ou resoluções formalmente decididas no encontro.

5. **Próximos passos**  
   Indique o que precisa ser feito após a reunião.

---

### Instruções específicas ###

- Use **linguagem formal e objetiva**.
- **Não invente informações**: apenas utilize dados reais da transcrição.
- Quando algum item estiver indefinido (como responsável ou prazo), informe como **"Não especificado"**.
- Formate a saída em **Markdown**, mantendo a tabela das tarefas como mostrado acima.

---"""
        )

    audio_part = types.Part.from_bytes(
        data=audio_bytes,
        mime_type=mime_type,
    )

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=[prompt, audio_part],
    )

    return getattr(response, "text", str(response))


# =========================================
# Upload de Áudio (container estilizado)
# =========================================

with st.container(border=True):
    st.markdown("### 🎧 Upload de Áudio")
    st.write("Envie seu arquivo e escolha o tipo de processamento.")

    modo_label = st.radio(
        "Modo de saída:",
        ("Transcrição literal", "Resumo de reunião"),
        horizontal=True,
    )
    modo_interno = "transcricao" if modo_label == "Transcrição literal" else "resumo"

    arquivo = st.file_uploader(
        "Selecione um arquivo de áudio",
        type=["wav", "mp3", "m4a", "ogg", "flac"],
    )

    if arquivo is not None:
        ext = arquivo.name.split(".")[-1].lower()
        mime_map = {
            "wav": "audio/wav",
            "mp3": "audio/mpeg",
            "m4a": "audio/mp4",
            "ogg": "audio/ogg",
            "flac": "audio/flac",
        }
        mime_type = mime_map.get(ext, "audio/wav")

        st.audio(arquivo, format=mime_type)
        st.info(f"Arquivo recebido: **{arquivo.name}** ({mime_type})")

        if st.button("🚀 Processar com Gemini"):
            audio_bytes = arquivo.read()

            with st.spinner("Processando..."):
                resultado = transcrever_audio_bytes(
                    audio_bytes, mime_type, modo_interno
                )

            st.session_state["resultado"] = resultado
            st.success("Processamento concluído!")


# =========================================
# Resultado (container estilizado + botão copiar)
# =========================================

if "resultado" in st.session_state:

    with st.container(border=True):
        st.markdown("### 📝 Resultado")
        texto = st.session_state["resultado"]

        # st.markdown(
        #     f"""
        #     <div style="
        #         border:1px solid #ccc;
        #         padding:15px;
        #         border-radius:10px;
        #         # background-color:#fafafa;
        #         font-size:16px;
        #     ">
        #     {texto}
        #     </div>
        #     """,
        #     unsafe_allow_html=True,
        # )
        # # Botão de copiar
        st.text_area("Copiar resultado", texto, height=200)
        st.write("Clique dentro do box acima e aperte **CTRL+C** ou **CMD+C**.")

