from re import template
import dash
from dash.dependencies import Input, Output, State
from dash import Dash, html, dcc
import pandas as pd
import numpy as np 
import matplotlib.pyplot as plt 
import plotly.express as px 
import seaborn as sns 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import dash_bootstrap_components as dbc
app = Dash(__name__,external_stylesheets=[dbc.themes.CYBORG])
app.title = "Z by HP worldwide data!"
server = app.server

#reading csv files
fires = pd.read_csv('./fires_data_11-29-2021.csv')
energy = pd.read_csv('./energy_use_data_11-29-2021.csv')
land = pd.read_csv('./land_cover_data_11-30-2021.csv')
temp = pd.read_csv('./temperature_change_data_11-29-2021.csv')
waste =  pd.read_csv( './waste_disposal_data_11-29-2021.csv')

grouped_land = land.groupby(["Area", "Area Code (ISO3)", "Year"])["Value"].sum().reset_index()

md_text = """
# Z by HP first!
This visualizations are made with [Dash](https://plot.ly/dash/) and [Plotly](https://plot.ly/python/).
In this I'll create a simple dashboard with dash and plotly. 
"""

app.theme = 'dark'
app.layout = html.Div([
    dcc.Markdown(children = md_text),
    dcc.Slider(
        energy['Year'].min(),
        energy['Year'].max(),
        step=None,
        value=energy['Year'].min(),
        marks={str(year): str(year) for year in energy['Year'].unique()},
        id='slider'
    ),
    dcc.Graph(id="graph-2"),
    dcc.Markdown(children = "## Temperature change in top 4 Economics"), 
    dcc.Graph(id="graph-3"),
    dcc.Markdown(children = "## grouped land coverage"), 
    dcc.Graph(id='graph', figure = px.choropleth(
        
    grouped_land,
    hover_data=['Area', 'Value'],
    locations = "Area Code (ISO3)",template = "plotly_dark",height=1000)),
    
    # dcc.Dropdown(fig.update_layout(height=300, margin={"r":0,"t":0,"l":0,"b":0})

    #       energy["Year"].unique(),
    #             1990,
    #             id='dropdown')
])
@app.callback(Output("graph-3", "figure"), Input("slider", "value"))
def create_figure(ins):
    areas_to_keep = ["China", "Germany", "Japan", "United States of America"]

    # Filter the data
    evolution = temp[(temp["Flag Description"] != "Data Not Available") & 
                    (temp["Months"] == "Meteorological year") & 
                    (temp["Area"].isin(areas_to_keep))].reset_index(drop=True)

    # Rename some Areas
    evolution["Area"] = evolution["Area"].replace(to_replace=["United States of America"],
                                                value=["United States"])

    # Group by Area and Year
    evolution = evolution.groupby(["Area", "Year"])["Value"].mean().reset_index()
    # Set the general figure size

    # Plot the initial linechart
    fig = px.line(evolution, x="Year", y="Value", color = "Area")
    fig.update_layout( template="plotly_dark",)
    # Add a general title
    # plt.suptitle("Temperature Change for top 4 Economies (in 2021)", fontsize=25, weight="bold")
    # plt.title("- with respect to 1951-1980 baseline climatology -", fontsize=19, style="italic")

    # # Format axis labels
    # plt.xlabel("Year", fontsize=19)
    # plt.ylabel("Temperature Change (℃)", fontsize=19)
    return fig

@app.callback(Output('graph-2', 'figure'),Input('slider', 'value'))
def create_energy_graph(input_year):
    print("input_year", input_year)
    print(energy.Year.unique())
    areas_to_keep = ["China","Germany", "Japan", "United States of America"]
    # Filter the    
    energy_df = energy[(energy["Area"].isin(areas_to_keep)) & 
                    (energy["Year"]==input_year)].reset_index(drop=True)

    # Rename some Areas
    energy_df["Area"] = energy_df["Area"].replace(to_replace=["United States of America"],
                                            value=["United States"])

    # Group by Area and Item
    energy_df = energy_df.groupby(["Area", "Item"])["Value"].mean().reset_index()

    # Compute percentage per country
    totals = energy_df.groupby("Area")["Value"].sum().reset_index()
    energy_df = pd.merge(energy_df, totals, on="Area")

    energy_df["Perc"] = energy_df["Value_x"] / energy_df["Value_y"]
    energy_df["Perc"] = energy_df["Perc"].apply(lambda x: round(x*100, 2))
    # Create the layout of the chart
    title = f"<b>CO2 Emissions in {input_year}</b><br><sup>Per Top 4 Countries and Energy Industries</sup>"
    # Create the figure
    fig = go.Figure()

    # Create the base Scatter Plot
    fig.add_trace(go.Scatter(
       
        # X and Y axis
        x=energy_df["Area"],
        y=energy_df["Item"],
       
        # The marker shape and size
        mode='markers', 
        hovertemplate="Country: %{x}<br>" +
                    "Industry: %{y}<br>" +
                    "CO2 Emissions: %{marker.size:,}%" +
                    "<extra></extra>",
        
        marker=dict(color=energy_df["Perc"],
                    size=energy_df["Perc"],
                    showscale=True,
                    colorbar=dict(title='%CO2<br>Emissions'),
                    opacity=0.7,
                    colorscale='Jet'),
        
    ))

    # Update the x and y axis
    fig.update_xaxes(showline=True, linewidth=0.1, linecolor='#c9c4c3', gridcolor='#c9c4c3',
                    tickfont=dict(size=14,), 
                    title="", showgrid=True, tickangle=0)

    fig.update_yaxes(showline=False, linewidth=0.1, gridcolor='#c9c4c3',
                    tickfont=dict(size=14, ), 
                    title="", showgrid=True,  )
    fig.update_layout( template="plotly_dark",title="co2 emissions")
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)  # debug=True


