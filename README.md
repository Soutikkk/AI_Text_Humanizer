# ✨ AI Text Humanizer

A simple, powerful, and highly extensible Python application designed to transform rigid, predictable, and robotic AI-generated text (from tools like ChatGPT, Claude, etc.) into natural, fluid, and conversational human-like writing.

It offers both a **Command-Line Interface (CLI)** and a **Streamlit Web Dashboard** featuring live statistics, styling, strength configuration, and dynamic export capabilities.

---

## 🚀 Key Features

* **Advanced Local Heuristics Engine**: Run it completely offline. No API keys or external services required by default.
* **Repetitive Word Replacement**: Identifies overused words and replaces them with contextual synonyms using a hybrid system (NLTK WordNet + curated local dictionary fallback).
* **Robotic Phrase Remapping**: Smooths out typical "AI-signature" transition phrases (e.g., *"In conclusion"*, *"Furthermore"*, *"It is important to note that"*) and replaces them with natural, human equivalents.
* **Flow & Sentence Variation**: Analyzes sentence lengths and automatically splits long, monotonous compound sentences into varied human-like structures.
* **Humanization Strength (Low, Medium, High)**:
  * **Low**: Keeps original structure, correcting only major robotic phrases.
  * **Medium**: Applies balanced rephrasing, contractions, and structure splitting.
  * **High**: Fully humanizes writing with conversational fillers (*"Honestly, "*, *"Well, "*) and aggressive flow variation.
* **Modular OpenAI Integration**: Ready to extend. Enter your OpenAI API Key directly in the web app or CLI to utilize state-of-the-art LLM humanization.
* **Streamlit Web GUI**: Beautiful dark-mode design with side-by-side text comparisons, character/word change statistics, and file downloads.
* **Client-Side Copy**: Quick copy-to-clipboard widget embedded natively inside the browser interface.

---

## 🛠️ Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/Soutikkk/AI_Text_Humanizer.git
   cd AI_Text_Humanizer
   ```

2. **Set up a Virtual Environment** (Recommended):
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   *Note: NLTK corpora will automatically be downloaded on the first run of the engine.*

---

## 💻 Running the Application

### 1. Interactive CLI Mode
To start the interactive prompt loop:
```bash
python main.py
```
This launches a guided walk-through in your terminal:
1. Input your raw AI text.
2. Select the Humanization Strength (`Low`, `Medium`, `High`).
3. Select Heuristic or OpenAI engine.
4. View side-by-side comparison stats.
5. Export output to a `.txt` file.

**CLI Argument Mode**:
You can also automate the script from standard terminal arguments:
```bash
python main.py --input raw_ai.txt --output humanized.txt --strength High
```

### 2. Streamlit Web Dashboard
To launch the beautiful dark-themed web browser interface:
```bash
streamlit run app.py
```
This will open `http://localhost:8501` in your browser. You can input text, adjust parameters via the sidebar, and copy or download results with single clicks.

---

## 🧪 Running Unit Tests
To verify all text engine modules and edge cases are operating correctly, execute:
```bash
python -m unittest test_humanizer.py
```

---

## 🧠 How the Heuristics Engine Works

```
Raw AI Text 
   │
   ▼
1. Robotic Phrase Replacement ──► Replaces "furthermore" with "also", etc. (probabilistic)
   │
   ▼
2. Contraction Adjustment ─────► Maps "it is" to "it's" based on strength
   │
   ▼
3. Sentence Length Splitting ──► Breaks down >20-word conjunction clauses (e.g. ", and")
   │
   ▼
4. Conversational Filler ──────► (High Strength) Adds natural conversational transitions
   │
   ▼
5. Synonym Replacements ──────► Replaces subsequent repeated words (NLTK/Local Dict)
   │
   ▼
Humanized Output Text
```

---

## 📝 License
This project is open-source and available under the [MIT License](LICENSE).
