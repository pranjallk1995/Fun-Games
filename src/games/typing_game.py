import random
import string
import time
import pandas as pd
import streamlit as st
from st_keyup import st_keyup


class TypingGameApp:
    """
    Streamlit app for Typing Master.
    """

    def __init__(self) -> None:
        self.init_session_state()

    def init_session_state(self):
        if "typing_start_time" not in st.session_state:
            st.session_state.typing_start_time = None
        if "typing_challenge" not in st.session_state:
            st.session_state.typing_challenge = ""
        if "typing_results" not in st.session_state:
            st.session_state.typing_results = []
        if "include_numbers" not in st.session_state:
            st.session_state.include_numbers = False
        if "include_capitals" not in st.session_state:
            st.session_state.include_capitals = False
        if "include_punctuations" not in st.session_state:
            st.session_state.include_punctuations = False

    def show_checkboxes(self):
        """
        Inline checkboxes stored in session state.
        Changing any checkbox regenerates the challenge immediately.
        """
        col1, col2, col3 = st.columns(3)
        changed_numbers = col1.checkbox(
            "Include Numbers", value=st.session_state.include_numbers
        )
        changed_capitals = col2.checkbox(
            "Include Capitals", value=st.session_state.include_capitals
        )
        changed_punctuations = col3.checkbox(
            "Include Punctuations", value=st.session_state.include_punctuations
        )

        # If any option changed, update session state and regenerate challenge
        if (changed_numbers != st.session_state.include_numbers or
            changed_capitals != st.session_state.include_capitals or
            changed_punctuations != st.session_state.include_punctuations):
            st.session_state.include_numbers = changed_numbers
            st.session_state.include_capitals = changed_capitals
            st.session_state.include_punctuations = changed_punctuations
            st.session_state.typing_challenge = self.generate_challenge()

    def generate_challenge(self, length: int = 10) -> str:
        """
        Generate a random typing challenge string based on session state options.
        """
        chars = string.ascii_lowercase
        if st.session_state.include_numbers:
            chars += string.digits
        if st.session_state.include_capitals:
            chars += string.ascii_uppercase
        if st.session_state.include_punctuations:
            chars += string.punctuation
        return "".join(random.choice(chars) for _ in range(length))

    def input_text(self):
        """
        Render typing challenge and capture keystrokes in real time.
        """
        if not st.session_state.typing_challenge:
            st.session_state.typing_challenge = self.generate_challenge()

        st.markdown(f"### Challenge: `{st.session_state.typing_challenge}`")

        user_input = st_keyup("Type the above string:", key="typing_input")

        if user_input:
            # Start timer when typing begins
            if st.session_state.typing_start_time is None:
                st.session_state.typing_start_time = time.time()

            if len(user_input) >= len(st.session_state.typing_challenge):
                elapsed = time.time() - st.session_state.typing_start_time
                st.toast(f"Time: {elapsed:.1f}s", icon=":material/info:")
                valid_input = True if user_input == st.session_state.typing_challenge else False
                st.session_state.typing_results.append(
                    (st.session_state.typing_challenge, valid_input, f"{elapsed:.1f}s")
                )
                # Reset for next challenge
                st.session_state.typing_challenge = self.generate_challenge()
                st.session_state.typing_start_time = None
            else:
                # Live character highlighting
                highlighted = ""
                for i, char in enumerate(user_input):
                    if i < len(st.session_state.typing_challenge):
                        if char == st.session_state.typing_challenge[i]:
                            highlighted += f"<span style='color:green'>{char}</span>"
                        else:
                            highlighted += f"<span style='color:red'>{char}</span>"
                    else:
                        highlighted += f"<span style='color:gray'>{char}</span>"
                st.markdown(f"**Live check:** {highlighted}", unsafe_allow_html=True)

    def results(self):
        """
        Display results table with challenges, correctness, and time taken.
        """
        if st.session_state.typing_results:
            df = pd.DataFrame(
                st.session_state.typing_results, columns=["Challenge", "Correct", "Time"]
            )
            st.dataframe(df[::-1], hide_index=True, width="stretch", height=145)

    def run(self):
        st.title(":material/keyboard: Typing Master Game")
        self.show_checkboxes()
        self.input_text()
        self.results()
