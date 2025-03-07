import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
import requests

# Download and save dataset
url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"
response = requests.get(url)
with open("spacex_launch_dash.csv", "wb") as file:
    file.write(response.content)

# Load SpaceX dataset
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize Dash app
app = dash.Dash(__name__)

# Layout of the dashboard
app.layout = html.Div([
    html.H1("SpaceX Launch Dashboard", style={'textAlign': 'center', 'color': '#503D36', 'fontSize': 40}),
    
    dcc.Dropdown(id='site-dropdown',
                 options=[{'label': 'All Sites', 'value': 'ALL'}] + 
                         [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    
    html.Br(),
    dcc.Graph(id='success-pie-chart'),
    
    html.Br(),
    dcc.RangeSlider(id='payload-slider',
                    min=min_payload, max=max_payload, step=1000,
                    marks={int(x): str(int(x)) for x in range(int(min_payload), int(max_payload)+1, 1000)},
                    value=[min_payload, max_payload]),
    
    html.Br(),
    dcc.Graph(id='success-payload-scatter-chart')
])

# Callback for pie chart
@app.callback(
    Output('success-pie-chart', 'figure'),
    Input('site-dropdown', 'value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        fig = px.pie(spacex_df, names='Launch Site', values='class', title='Total Success Launches by Site')
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]
        fig = px.pie(filtered_df, names='class', title=f'Success vs Failure for {selected_site}')
    return fig

# Callback for scatter plot
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'),
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
    if selected_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version',
                     title=f'Payload vs. Outcome for {selected_site}')
    return fig

# Run app
if __name__ == '__main__':
    app.run_server(debug=True)
