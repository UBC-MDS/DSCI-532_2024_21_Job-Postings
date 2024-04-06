from dash import Dash, html, dcc
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd





# Load the dataset
#df = pd.read_csv('../data/processed/cleaned_job_postings.csv')

df = pd.read_csv('data/processed/cleaned_job_postings.csv')

jobs_by_region = df['region'].value_counts().reset_index()
jobs_by_region.columns = ['region', 'count']




# Edit by A.Z.
from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

subdf=df[df['pay_period']=="YEARLY"]
subdf1 = subdf.groupby('state_code')['max_salary'].median()
subdf2 = subdf1.reset_index()  
subdf2.columns = ['state_code', 'max_salary']  


fig_map = go.Figure(data=go.Choropleth(
    locations=subdf2['state_code'],
    z=subdf2['max_salary'].astype(float),
    locationmode='USA-states',
    colorscale="Viridis",
    autocolorscale=True,
    text=subdf2['state_code'], # hover text
    marker_line_color='black', # line markers between states
    colorbar_title="USD"
))


fig_map.update_layout(
    title_text='2023 US Job Postings by State',
    geo = dict(
        scope='usa',
        projection=go.layout.geo.Projection(type = 'albers usa'),
        showlakes=True, # lakes
        lakecolor='rgb(255, 255, 255)'),
)








# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Plot for jobs_by_region
region_colors = {
    'West': 'blue',
    'Northeast': 'green',
    'Southeast': 'red',
    'Midwest': 'pink',
    'Southwest': 'orange',
}
bar_colors = [region_colors[region] for region in jobs_by_region['region']]

jobs_by_region_figure = go.Figure(
    data=[
        go.Bar(
            x=jobs_by_region['region'],
            y=jobs_by_region['count'],
            marker=dict(color=bar_colors),
        )
    ],
    layout=go.Layout(
        title='Number of Job Postings by Region',
        xaxis=dict(title='Region'),
        yaxis=dict(title='Number of Job Postings'),
        hovermode='closest'
    )
)






# Define the layout of the app
app.layout = html.Div([
    html.H1('U.S. Job Postings Visualization', style={'textAlign': 'center'}),
    


    # Edit by A.Z.
    html.Div([
    dcc.Graph(figure=fig_map)]),

    # Filters Section
    html.Div([
        html.Label('Minimum Salary'),
        dcc.Slider(
            id='min-salary-slider',
            min=0,
            max=100000,
            step=1000,
            value=30000,
            marks={i: '${:,.0f}'.format(i) if i % 20000 == 0 else '' for i in range(0, 100001, 10000)},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        html.Label('Maximum Salary'),
        dcc.Slider(
            id='max-salary-slider',
            min=0,
            max=100000,
            step=1000,
            value=70000,
            marks={i: '${:,.0f}'.format(i) if i % 20000 == 0 else '' for i in range(0, 100001, 10000)},
            tooltip={"placement": "bottom", "always_visible": True},
        ),
        html.Label('Job Type'),
        dbc.Checklist(
            options=[
                {"label": "Full-time", "value": "Full-time"},
                {"label": "Part-time", "value": "Part-time"},
                {"label": "Contract", "value": "Contract"},
            ],
            value=["Full-time"],
            id='job-type-checklist',
            inline=True,
        ),
        html.Label('Experience Level'),
        dbc.Checklist(
            options=[
                {"label": "Entry Level", "value": "Entry level"},
                {"label": "Mid-Senior Level", "value": "Mid-Senior level"},
            ],
            value=["Entry level"],
            id='experience-level-checklist',
            inline=True,
        ),
    ], style={'width': '20%', 'display': 'inline-block', 'verticalAlign': 'top'}),

    # Map and Charts Section
    html.Div([
        dcc.Graph(
            id='job-postings-map',
            figure=go.Figure(),  # Placeholder empty figure
            style={'width': '40%', 'display': 'inline-block'}
        ),
        html.Div([
            dcc.Graph(
                id='average-salary-region',
                figure=go.Figure(),  # Placeholder empty figure
                style={'width': '30%', 'display': 'inline-block'}
            ),
            dcc.Graph(
                id='proportion-job-postings',
                figure=go.Figure(),  # Placeholder empty figure
                style={'width': '30%', 'display': 'inline-block'}
            ),
            dcc.Graph(
                id='jobs-by-region-bar-chart',
                figure=jobs_by_region_figure,
                style={'width': '30%', 'display': 'inline-block'}
            ),
        ]),
    ], style={'width': '80%', 'display': 'inline-block'}),
    
    # Footer
    html.Div([
        html.P('Data provided by XYZ Corp', style={'textAlign': 'center'}),
    ]),
])

# Server side callbacks/reactivity
# Callback for updating the bar chart based on the filters
@app.callback(
    Output('jobs-by-region-bar-chart', 'figure'),
    [Input('min-salary-slider', 'value'),
     Input('max-salary-slider', 'value'),
     Input('job-type-checklist', 'value'),
     Input('experience-level-checklist', 'value')]
)
def update_bar_chart(min_salary, max_salary, selected_job_types, selected_experience_levels):
    # Start with the full DataFrame
    filtered_df = df.copy()
    
    # Apply salary filter
    filtered_df = filtered_df[(filtered_df['min_salary'] >= min_salary) & (filtered_df['max_salary'] <= max_salary)]
    
    # Apply job type filter
    if selected_job_types:
        filtered_df = filtered_df[filtered_df['formatted_work_type'].isin(selected_job_types)]
    
    # Apply experience level filter
    if selected_experience_levels:
        filtered_df = filtered_df[filtered_df['formatted_experience_level'].isin(selected_experience_levels)]
    
    # Group by region and count the job postings
    jobs_by_region = filtered_df['region'].value_counts().reset_index()
    jobs_by_region.columns = ['region', 'count']

    # Generate the colors for the bar chart dynamically
    bar_colors = [region_colors.get(region, 'gray') for region in jobs_by_region['region']]
    
    # Create a new figure
    figure = go.Figure(
        data=[
            go.Bar(
                x=jobs_by_region['region'],
                y=jobs_by_region['count'],
                marker=dict(color=bar_colors),
            )
        ],
        layout=go.Layout(
            title='Number of Job Postings by Region',
            xaxis=dict(title='Region'),
            yaxis=dict(title='Number of Job Postings'),
            hovermode='closest'
        )
    )
    return figure

# Run the app/dashboard
if __name__ == '__main__':
    app.run_server(debug=True)
