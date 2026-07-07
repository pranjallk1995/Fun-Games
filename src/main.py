import streamlit as st

from games.typing_game import TypingGameApp
from games.worldmap_game import WorldMapGameApp

if __name__ == "__main__":

    st.set_page_config(
        page_title="Games",
        layout="wide"
    )

    st.sidebar.title(":material/sports_esports: Game Selector")

    # Define all available games here
    games = {
        "Typing Master": lambda: TypingGameApp().run(),
        "World Map": lambda: WorldMapGameApp().run(),
        # Add more games easily:
        # "Sudoku": sudoku_game
    }

    # Render buttons dynamically
    for game_name, game_func in games.items():
        if st.sidebar.button(f"{game_name}", use_container_width=True):
            st.session_state.selected_game = game_name

    # Default selection if none yet
    if "selected_game" not in st.session_state:
        st.session_state.selected_game = list(games.keys())[0]  # first game in dict

    # Run the chosen game
    games[st.session_state.selected_game]()
