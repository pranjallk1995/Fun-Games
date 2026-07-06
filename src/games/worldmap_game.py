import time
import pandas as pd
import config as cfg
import streamlit as st
import country_converter as coco
import plotly.graph_objects as go


class WorldMap:
    """
    Handles map rendering and country highlighting logic.
    Responsible for converting country names to ISO codes,
    updating map properties, and displaying highlighted countries.
    """

    def __init__(self) -> None:
        """
        Initialize the world map figure and load country codes.
        """
        self.world_map = go.Figure(go.Scattergeo())
        self.coco = coco.CountryConverter()

        # Use full ISO3 list from country_converter (195+ countries)
        self.country_codes = pd.DataFrame(
            {
                "country": self.coco.data["name_short"],
                "iso_alpha": self.coco.data["ISO3"]
            }
        ).drop_duplicates()

    def normalize_country_to_iso3(self, name: str) -> str:
        """
        Convert a country name to its ISO3 code.

        Args:
            name (str): Country name entered by the user.

        Returns:
            str: ISO3 code if valid, otherwise None.
        """
        if not name:
            return None
        iso3 = self.coco.convert(names=name, to="ISO3")
        return iso3 if iso3 != "not found" else None

    def update_map_properties(self) -> None:
        """
        Configure base map appearance (colors, borders, etc.).
        """
        self.world_map.update_geos(
            bgcolor=cfg.BORDER_COLOR,
            showcountries=True, countrycolor=cfg.BORDER_COLOR,
            showcoastlines=True, coastlinecolor=cfg.BORDER_COLOR,
            showland=True, landcolor=cfg.LAND_COLOR,
            showocean=True, oceancolor=cfg.OCEAN_COLOR
        )
        self.world_map.update_layout(
            autosize=False,
            margin={"r":0,"t":0,"l":0,"b":0}
        )

    def highlight_country(self, iso_code: str) -> None:
        """
        Highlight a guessed country on the map.

        Args:
            iso_code (str): ISO3 code of the guessed country.
        """
        if iso_code and iso_code != "not found":
            self.world_map.add_trace(
                go.Choropleth(
                    locations=[iso_code],
                    z=[1],
                    colorscale=[[0, cfg.GUESSED_COLOR], [1, cfg.GUESSED_COLOR]],
                    showscale=False
                )
            )

    def show_world_map(self, guessed_iso_codes: list[str]) -> None:
        """
        Display the world map with all guessed countries highlighted.

        Args:
            guessed_iso_codes (list[str]): List of ISO3 codes guessed so far.
        """
        if not hasattr(self, "_initialized") or not self._initialized:
            self.update_map_properties()
            self._initialized = True
        self.world_map.data = []  
        for iso in guessed_iso_codes:
            self.highlight_country(iso)
        st.plotly_chart(self.world_map, width="stretch")


class WorldMapGameApp:
    """
    Encapsulates the Streamlit app/game functionality.
    Handles session state, UI rendering, user input, progress tracking,
    and displaying guessed countries.
    """

    def __init__(self):
        """
        Initialize the app by creating a WorldMap instance
        and setting up session state variables.
        """
        self.wm_obj = WorldMap()
        self.init_session_state()

    def init_session_state(self):
        """
        Initialize Streamlit session state variables for game state,
        start time, guessed countries, and input box.
        """
        if "game_active" not in st.session_state:
            st.session_state.game_active = False
        if "start_time" not in st.session_state:
            st.session_state.start_time = None
        if "guessed_iso_codes" not in st.session_state:
            st.session_state.guessed_iso_codes = []
        if "input_box" not in st.session_state:
            st.session_state.input_box = ""

    def start_stop_buttons(self):
        """
        Render Start/Stop buttons and handle game state transitions.
        """
        col1, col2 = st.columns(2)
        if col1.button(":material/play_arrow: Start", width="stretch"):
            st.session_state.game_active = True
            st.session_state.start_time = time.time()
            st.session_state.guessed_iso_codes = []

        if col2.button(":material/stop: Stop", width="stretch"):
            st.session_state.game_active = False
            if st.session_state.start_time:
                elapsed = time.time() - st.session_state.start_time
                st.success(f":material/timer: Time taken: {elapsed:.1f} seconds")
                st.error(
                    f"""
                        You guessed {len(st.session_state.guessed_iso_codes)}/{len(self.wm_obj.country_codes)}
                    """
                )

    def process_guess(self):
        """
        Process the user's guess, normalize to ISO3,
        add to guessed list if valid, and clear the textbox.
        """
        guess = st.session_state.input_box
        iso_code = self.wm_obj.normalize_country_to_iso3(guess)
        if not iso_code:
            st.toast("Invalid country name.", icon=":material/warning:")
        elif iso_code in st.session_state.guessed_iso_codes:
            st.toast("You already guessed this country.", icon=":material/info:")
        else:
            st.session_state.guessed_iso_codes.append(iso_code)
            st.toast(f"{guess} added!", icon=":material/check_circle:")
        st.session_state.input_box = ""

    def input_and_progress(self):
        """
        Render the input box for guesses and show progress bar
        indicating percentage of countries guessed.
        """
        if st.session_state.game_active:
            st.text_input("Enter a country name:", key="input_box", on_change=self.process_guess)

            total_countries = len(self.wm_obj.country_codes)
            guessed_count = len(st.session_state.guessed_iso_codes)
            progress = guessed_count / total_countries
            st.progress(progress, text=f"{guessed_count}/{total_countries} countries guessed")

    def guessed_countries_table(self):
        """
        Display a table of all guessed countries with friendly names.
        """
        if st.session_state.guessed_iso_codes:
            guessed_names = [
                self.wm_obj.coco.convert(names=iso, to="name_short")
                for iso in st.session_state.guessed_iso_codes
            ]
            df = pd.DataFrame(guessed_names[::-1])
            df.columns = ["Guessed Countries"]
            st.dataframe(df, hide_index=True, width="stretch", height=145)

    def run(self):
        """
        Run the Streamlit app by orchestrating UI components:
        title, buttons, input, progress bar, map, and guessed list.
        """
        st.title(":material/map_search: World Map Game")
        self.start_stop_buttons()
        self.input_and_progress()
        self.wm_obj.show_world_map(st.session_state.guessed_iso_codes)
        self.guessed_countries_table()
