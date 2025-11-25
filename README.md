# 🎙️ MeetSummarizeAI

MeetSummarizeAI é um app em **Streamlit** para **transcrever** e **resumir reuniões** a partir de arquivos de áudio, usando a API do **Gemini**.

A ideia é simples: você sobe o áudio, escolhe se quer **transcrição literal** ou **resumo estruturado**, e o app faz o resto.

---

## ✨ Funcionalidades

- Upload de arquivos de áudio (`.wav`, `.mp3`, `.m4a`, `.ogg`, `.flac`)
- Escolha de modo de saída:
  - **Transcrição literal**
  - **Resumo de reunião** com:
    - Contexto  
    - Decisões  
    - Pendências  
    - Próximos passos
- Player de áudio embutido
- Uso do modelo **`gemini-2.0-flash-lite`**
- Campo para **configuração da API Key do Gemini**
- Botão para **salvar a API Key no navegador** (via `localStorage`)
- Área de resultado com **text area copiável** (CMD/CTRL + C)

---

## 🧱 Stack Tecnológica

- [Python](https://www.python.org/) (>= 3.9)
- [Streamlit](https://streamlit.io/)
- [`google-genai`](https://pypi.org/project/google-genai/)
- [`python-dotenv`](https://pypi.org/project/python-dotenv/)
- [`streamlit-js-eval`](https://pypi.org/project/streamlit-js-eval/)

---

## 📦 Instalação

Clone o repositório e entre na pasta do projeto:

```bash
git clone <URL_DO_REPOSITORIO>
cd MeetingTranscriber  # ou o nome da pasta/projeto