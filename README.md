# 🎮 Fun-Games

A collection of interactive games built with **Streamlit** and **Plotly**, including:
- 🌍 **World Map Game** – guess countries and see them highlighted on a live map.
  ![src/assets/wordl_map.png](https://github.com/pranjallk1995/Fun-Games/blob/0120aeb3cbfbc841a160e72b17c6db4932c9cd05/src/assets/world_map.png)
- ⌨️ **Typing Master Game** – practice typing speed and accuracy with real-time keystroke checks.

    *work in progress*

---

## ⚙️ Method 1: Local Virtual Environment

1. **Navigate to project root**

    `cd Fun-Games`
2. **Create a virtual environment**

    `python3 -m venv .venv`
3. **Activate the environment**

    - Linux/macOS:

        `source .venv/bin/activate`

    - Windows (PowerShell):

        `.venv\Scripts\Activate.ps1`

4. **Install dependencies**

    `pip install -r src/requirements.txt`
5. **Run the app**

    `streamlit run src/main.py`

**By default, the app will be available at: http://localhost:8501**

---

## 🐳 Method 2: Docker Compose

1. **Navigate to project root**

    `cd Fun-Games`
2. **Run in detached mode**

    `docker compose up -d`

**By default, the app will be available at: http://localhost:16969**
