import os
import json
import random
import config as cfg
import streamlit as st
import country_converter as coco

class FlagGameApp:
    def __init__(self):
        json_file = os.path.join(cfg.FLAG_DIR, cfg.FLAG_JSON_FILE)
        with open(json_file, "r", encoding="utf-8") as json_file:
            self.flag_map = json.load(json_file)

        self.codes = list(self.flag_map.keys())
        self.coco = coco.CountryConverter()
        self.init_session_state()

    def init_session_state(self):
        if "flag_active" not in st.session_state:
            st.session_state.flag_active = False
        if "current_flag" not in st.session_state:
            st.session_state.current_flag = None
        if "score" not in st.session_state:
            st.session_state.score = 0
        if "attempts" not in st.session_state:
            st.session_state.attempts = 0

    def normalize_guess(self, guess: str) -> str | None:
        """
        Normalize user guess to ISO3 code using country_converter.
        Returns ISO3 code if valid, else None.
        """
        if not guess:
            return None
        iso3 = self.coco.convert(names=guess, to="ISO3")
        return iso3 if iso3 != "not found" else None

    def start_stop_buttons(self):
        col1, col2 = st.columns(2)
        if col1.button(":material/play_arrow: Start", use_container_width=True):
            st.session_state.flag_active = True
            st.session_state.score = 0
            st.session_state.attempts = 0
            self.next_flag()

        if col2.button(":material/stop: Stop", use_container_width=True):
            st.session_state.flag_active = False
            st.success(f"Final Score: {st.session_state.score}/{st.session_state.attempts}")

    def next_flag(self):
        st.session_state.current_flag = random.choice(self.codes)

    def show_flag(self):
        if st.session_state.current_flag:
            flag_path = os.path.join(cfg.FLAG_DIR, f"{st.session_state.current_flag.lower()}.png")
            st.image(flag_path, width=200)

    def process_guess(self):
        guess = st.session_state.flag_guess.strip()
        correct_name = self.flag_map[st.session_state.current_flag]

        st.session_state.attempts += 1

        guess_iso = self.normalize_guess(guess)
        correct_iso = self.normalize_guess(correct_name)
        if guess_iso and correct_iso and guess_iso == correct_iso:
            st.session_state.score += 1
            st.toast("Correct!", icon=":material/check_circle:")
        else:
            st.toast(f"Wrong! It was {correct_name}", icon=":material/error:")

        self.next_flag()
        st.session_state.flag_guess = ""

    def skip_flag(self):
        # Skip counts as an attempt but no score
        st.session_state.attempts += 1
        st.toast("Skipped!", icon=":material/skip_next:")
        self.next_flag()

    def show_name(self):
        # Reveal the correct answer, counts as an attempt but no score
        correct_name = self.flag_map[st.session_state.current_flag]
        st.session_state.attempts += 1
        st.toast(f"The flag was {correct_name}", icon=":material/info:")

    def run(self):
        st.title(":material/flag: Flag Guessing Game")
        self.start_stop_buttons()

        if st.session_state.flag_active:
            self.show_flag()
            st.text_input("Enter country name:", key="flag_guess", on_change=self.process_guess)

            # Extra controls
            col1, col2 = st.columns(2)
            if col1.button(":material/skip_next: Skip", use_container_width=True):
                self.skip_flag()
            if col2.button(":material/visibility: Show Name", use_container_width=True):
                self.show_name()

            st.info(f"Score: {st.session_state.score}/{st.session_state.attempts}")
