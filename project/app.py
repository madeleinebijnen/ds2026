from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from shiny import App, ui, render, reactive

DATA = Path(__file__).parent / "data" / "listings.csv"
listings = pd.read_csv(DATA)

# kolomnaam verschilt per versie van het bestand
BUURT = "neighbourhood_cleansed" if "neighbourhood_cleansed" in listings.columns else "neighbourhood"

# prijs kan tekst zijn ("$1,250.00"); bedragen zijn in euro
listings["price"] = pd.to_numeric(
    listings["price"].astype(str).str.replace(r"[$,]", "", regex=True), errors="coerce")
listings = listings.dropna(subset=["price"])

buurten = sorted(listings[BUURT].unique())

app_ui = ui.page_sidebar(
    ui.sidebar(ui.input_select("buurt", "Buurt", buurten), title="Filter"),
    ui.output_text("samenvatting"),
    ui.output_plot("prijs_plot"),
    title="Airbnb in Amsterdam: wat kost een nacht in jouw buurt?",
)

def server(input, output, session):

    @reactive.calc
    def gefilterd():
        return listings[listings[BUURT] == input.buurt()]

    @render.plot
    def prijs_plot():
        df = gefilterd()
        fig, ax = plt.subplots()
        ax.hist(df["price"].clip(upper=500), bins=40)
        ax.set_xlabel("Prijs per nacht (€, afgekapt op 500)")
        ax.set_ylabel("Aantal listings")
        return fig

    @render.text
    def samenvatting():
        df = gefilterd()
        return f"{len(df)} listings · mediane prijs €{df['price'].median():.0f}"

app = App(app_ui, server)