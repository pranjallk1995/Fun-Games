import time
import config as cfg
import pandas as pd
import streamlit as st

from ollama import Client
from st_keyup import st_keyup


class TypingGameApp:
    """
    Streamlit app for Typing Master.
    Provides typing challenges, tracks WPM, accuracy, and mistakes.
    """

    def __init__(self) -> None:
        self.init_session_state()
        self.client = Client(
            host="http://ollama-serve:11434",
            headers={"x-some-header": "some-value"},
        )

    def init_session_state(self):
        """
        Initialize all required session state variables.
        """
        defaults = {
            "typing_start_time": None,
            "typing_challenge": "",
            "typing_text": "",
            "typing_results": [],
            "include_numbers": False,
            "include_capitals": False,
            "include_punctuations": False,
            "typing_input": "",
            "typing_completed": False,
            "mistake_indices": set(),
        }
        for key, val in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = val

    def reset_game(self, new_challenge=True):
        """
        Reset typing state for a new challenge or restart.
        """
        st.session_state.typing_start_time = None
        st.session_state.typing_completed = False
        st.session_state.mistake_indices = set()
        if "typing_input" in st.session_state:
            del st.session_state["typing_input"]
        if new_challenge:
            st.session_state.typing_challenge, st.session_state.typing_text = self.generate_challenge()

    def show_checkboxes(self):
        """
        Render option checkboxes and regenerate challenge if changed.
        """
        col1, col2, col3 = st.columns(3)
        changed_numbers = col1.checkbox("Include Numbers", value=st.session_state.include_numbers)
        changed_capitals = col2.checkbox("Include Capitals", value=st.session_state.include_capitals)
        changed_punctuations = col3.checkbox("Include Punctuations", value=st.session_state.include_punctuations)

        if (
            changed_numbers != st.session_state.include_numbers
            or changed_capitals != st.session_state.include_capitals
            or changed_punctuations != st.session_state.include_punctuations
        ):
            st.session_state.include_numbers = changed_numbers
            st.session_state.include_capitals = changed_capitals
            st.session_state.include_punctuations = changed_punctuations
            self.reset_game(new_challenge=True)

    def generate_challenge(self) -> tuple[str, str]:
        """
        Generate a random typing challenge string and name using Ollama.
        """
        generate_numbers = "Add some numeric data" if st.session_state.include_numbers else "Do not add any numeric data"
        generate_capitals = "Add some words with capital letters, not all" if st.session_state.include_capitals else "Do not add any words with capital letters"
        generate_punctuations = "Add some punctuations" if st.session_state.include_punctuations else "Do not add any punctuations"

        text_prompt = f"""
            Give me a 50 word text to practice my typing with no explanations and introductory text.
            Consider the following:
                1. {generate_numbers}.
                2. {generate_capitals}.
                3. {generate_punctuations}.
                4. No newline characters.
        """
        response = self.client.chat(model="llama3", messages=[{"role": "user", "content": text_prompt}])
        name_prompt = "Give a random challenge name. One word only, no punctuation."
        name = self.client.chat(model="llama3", messages=[{"role": "user", "content": name_prompt}])

        challenge_text = response["message"]["content"].replace("\n", " ").strip()
        challenge_name = name["message"]["content"].strip().replace('"', "")
        return challenge_name, challenge_text

    def calculate_metrics(self, user_input: str) -> tuple[float, float, int]:
        """
        Calculate WPM, accuracy, and mistakes for the completed challenge.
        """
        elapsed = time.time() - st.session_state.typing_start_time
        word_count = len(user_input.split())
        wpm = (word_count / elapsed) * 60

        correct_chars = sum(
            1 for i, c in enumerate(user_input)
            if i < len(st.session_state.typing_text) and c == st.session_state.typing_text[i]
        )
        total_chars = len(st.session_state.typing_text)
        mistakes = len(st.session_state.mistake_indices)
        accuracy = ((total_chars - mistakes) / total_chars) * 100
        return wpm, accuracy, mistakes

    def input_text(self):
        """
        Render typing input, live feedback, and handle completion.
        """
        if not st.session_state.typing_challenge:
            st.session_state.typing_challenge, st.session_state.typing_text = self.generate_challenge()

        col1, col2 = st.columns([1, 9])
        if col1.button(":material/restart_alt:", use_container_width=True):
            self.reset_game(new_challenge=True)
            st.rerun()

        col2.markdown(f"### Challenge: `{st.session_state.typing_challenge}`")
        st.write(st.session_state.typing_text)

        user_input = st_keyup("Type the above text:", key="typing_input")

        if user_input and user_input.strip():
            if st.session_state.typing_start_time is None:
                self.reset_game(new_challenge=False)
                st.session_state.typing_start_time = time.time()

            if len(user_input) >= len(st.session_state.typing_text) and not st.session_state.typing_completed:
                wpm, accuracy, mistakes = self.calculate_metrics(user_input)
                st.toast(f"WPM: {wpm:.1f} | Accuracy: {accuracy:.1f}% | Mistakes: {mistakes}", icon=":material/info:")

                if wpm <= 300:
                    st.session_state.typing_results.append(
                        (st.session_state.typing_challenge, f"{wpm:.1f}", f"{accuracy:.1f}%", mistakes)
                    )
                    self.reset_game(new_challenge=True)
                    st.session_state.typing_completed = True
            else:
                checked_text = ""
                for i, char in enumerate(user_input):
                    if i < len(st.session_state.typing_text):
                        if char == st.session_state.typing_text[i]:
                            checked_text += f":green[{char if char != ' ' else '␣'}]"
                        else:
                            checked_text += f":red[{char if char != ' ' else '␣'}]"
                            st.session_state.mistake_indices.add(i)
                    else:
                        checked_text += f":gray[{char if char != ' ' else '␣'}]"
                st.write(f"**Live check:** {checked_text}")
                st.write(f"**Mistakes so far:** {len(st.session_state.mistake_indices)}")

    def results(self):
        """
        Display results table with challenges, WPM, Accuracy, and Mistakes.
        """
        if st.session_state.typing_results:
            df = pd.DataFrame(
                st.session_state.typing_results,
                columns=["Challenge", "WPM", "Accuracy", "Mistakes"],
            )
            st.dataframe(df[::-1], hide_index=True, width="stretch", height=cfg.RESULTS_HEIGHT)

    def run(self):
        """
        Run the full app: title, options, input, and results.
        """
        st.title(":material/keyboard: AI Powered Typing Game")
        self.show_checkboxes()
        self.input_text()
        self.results()
