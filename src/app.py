from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import plotly.graph_objs as go
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd


# Load the dataset
# df = pd.read_csv('../data/processed/cleaned_job_postings.csv')

df = pd.read_csv("data/processed/cleaned_job_postings.csv")

jobs_by_region = df["region"].value_counts().reset_index()
jobs_by_region.columns = ["region", "count"]

# preprocessing for avg salary graph
df["avg_salary"] = df[["min_salary", "max_salary"]].mean(axis=1)
avg_salary_by_region = df.groupby("region")["avg_salary"].mean().reset_index()
avg_salary_by_region = avg_salary_by_region.sort_values(
    by="avg_salary", ascending=False
)

# Preprocessing for avg min and max salary
avg_min_max_salaries_by_region = (
    df.groupby("region")
    .agg(avg_min_salary=("min_salary", "mean"), avg_max_salary=("max_salary", "mean"))
    .reset_index()
)


subdf = df[df["pay_period"] == "YEARLY"]
subdf1 = subdf.groupby("state_code")["max_salary"].median()
subdf2 = subdf1.reset_index()
subdf2.columns = ["state_code", "max_salary"]



# Initialize the app
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Plot for jobs_by_region
region_colors = {
    "West": "blue",
    "Northeast": "green",
    "Southeast": "red",
    "Midwest": "pink",
    "Southwest": "orange",
}
bar_colors = [region_colors[region] for region in jobs_by_region["region"]]

jobs_by_region_figure = go.Figure(
    data=[
        go.Bar(
            x=jobs_by_region["region"],
            y=jobs_by_region["count"],
            marker=dict(color=bar_colors),
        )
    ],
    layout=go.Layout(
        title="Number of Job Postings by Region",
        xaxis=dict(title="Region"),
        yaxis=dict(title="Number of Job Postings"),
        hovermode="closest",
    ),
)

# Plot for avg_salary_by_region
bar_colors_avg_sal = [
    region_colors[region] for region in avg_salary_by_region["region"]
]

avg_salary_by_region_fig = go.Figure()
avg_salary_by_region_fig.add_trace(
    go.Bar(
        x=avg_salary_by_region["region"],
        y=avg_salary_by_region["avg_salary"],
        marker=dict(color=bar_colors_avg_sal),
    )
)
avg_salary_by_region_fig.update_layout(
    title="Average Salary by Region",
    xaxis_title="Region",
    yaxis_title="Average Salary in USD",
    template="plotly_white",
)

# Plot for avg min and max by region
fig_avg_min_max_region = go.Figure(
    data=[
        go.Bar(
            name="Avg Min Salary",
            x=avg_min_max_salaries_by_region["region"],
            y=avg_min_max_salaries_by_region["avg_min_salary"],
        ),
        go.Bar(
            name="Avg Max Salary",
            x=avg_min_max_salaries_by_region["region"],
            y=avg_min_max_salaries_by_region["avg_max_salary"],
        ),
    ]
)
# Change the bar mode here if you prefer stacked bars
fig_avg_min_max_region.update_layout(
    barmode="group",
    title="Average Min and Max Salaries by Region",
    xaxis_title="Region",
    yaxis_title="Average Salary",
)


# Define the layout
app.layout = dbc.Container(
    [
        html.H1("U.S. Job Postings Visualization", className="text-center mb-4"),
        
        # Filters Section
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.H5('State Code'),
                        dcc.Dropdown(
                            id='state-dropdown',
                            options=[{'label': state, 'value': state} for state in df['state_code'].unique()],
                            multi=True,
                            value=['NY']
                        ),
                        html.Br(),

                        html.H5("Minimum Salary"),
                        dcc.Slider(
                            id='min-salary-slider',
                            min=0,
                            max=100000,
                            step=1000,
                            value=30000,
                            marks={i: f"${i:,}" for i in range(0, 100001, 20000)},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                        html.Br(),

                        html.H5("Maximum Salary"),
                        dcc.Slider(
                            id='max-salary-slider',
                            min=0,
                            max=100000,
                            step=1000,
                            value=70000,
                            marks={i: f"${i:,}" for i in range(0, 100001, 20000)},
                            tooltip={"placement": "bottom", "always_visible": True},
                        ),
                        html.Br(),

                        html.H5("Job Type"),
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
                        html.Br(),

                        html.H5("Experience Level"),
                        dbc.Checklist(
                            options=[
                                {"label": "Entry Level", "value": "Entry level"},
                                {"label": "Mid-Senior Level", "value": "Mid-Senior level"},
                            ],
                            value=["Entry level"],
                            id='experience-level-checklist',
                            inline=True,
                        ),
                    ],
                    md=4,
                ),
                dbc.Col(
                    [
                        dcc.Graph(id='job-posting', figure=jobs_by_region_figure)
                    ],
                    md=8,
                ),
            ],
            className="mb-4",
        ),
        
        # Additional Figures Section
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="average-salary-region"), md=4),
                dbc.Col(dcc.Graph(id="avg-min-max-salary-region"), md=4),
                dbc.Col(dcc.Graph(id="jobs-by-region-bar-chart"), md=4),
            ]
        ),
        
        # Footer
        dbc.Row(
            dbc.Col(
                [
                    html.P(
                        "This dashboard serves as a personalized job market navigator, offering insights based on job postings on Linkedin across the US in 2023. You can select the Job type, Experience level to see the overall salary range in specific regions. The dashboard is made by Andy Zhang, Prabhjit Thind, Sifan Zhang, Yan Zeng.",
                        className="text-center"
                    ),
                    html.P(
                        [
                            "Check the ",
                            html.A("repo", href="https://github.com/UBC-MDS/DSCI-532_2024_21_Job-Postings", target="_blank"),
                            "."
                        ],
                        className="text-center"
                    )
                ],
                width={"size": 10, "offset": 1},
                className="border-top pt-3"
            )
        ),
    ],
    fluid=True,
)



# Server side callbacks/reactivity
# Callback for updating the bar chart based on the filters
@app.callback(
    Output("jobs-by-region-bar-chart", "figure"),
    [
        Input("min-salary-slider", "value"),
        Input("max-salary-slider", "value"),
        Input("job-type-checklist", "value"),
        Input("experience-level-checklist", "value"),
    ],
)
def update_bar_chart(
    min_salary, max_salary, selected_job_types, selected_experience_levels
):
    # Start with the full DataFrame
    filtered_df = df.copy()

    # Apply salary filter
    filtered_df = filtered_df[
        (filtered_df["min_salary"] >= min_salary)
        & (filtered_df["max_salary"] <= max_salary)
    ]

    # Apply job type filter
    if selected_job_types:
        filtered_df = filtered_df[
            filtered_df["formatted_work_type"].isin(selected_job_types)
        ]

    # Apply experience level filter
    if selected_experience_levels:
        filtered_df = filtered_df[
            filtered_df["formatted_experience_level"].isin(selected_experience_levels)
        ]

    # Group by region and count the job postings
    jobs_by_region = filtered_df["region"].value_counts().reset_index()
    jobs_by_region.columns = ["region", "count"]

    # Generate the colors for the bar chart dynamically
    bar_colors = [
        region_colors.get(region, "gray") for region in jobs_by_region["region"]
    ]

    # Create a new figure
    figure = go.Figure(
        data=[
            go.Bar(
                x=jobs_by_region["region"],
                y=jobs_by_region["count"],
                marker=dict(color=bar_colors),
            )
        ],
        layout=go.Layout(
            title="Number of Job Postings by Region",
            xaxis=dict(title="Region"),
            yaxis=dict(title="Number of Job Postings"),
            hovermode="closest",
        ),
    )

    return figure


@app.callback(
    Output("average-salary-region", "figure"),
    [
        Input("min-salary-slider", "value"),
        Input("max-salary-slider", "value"),
        Input("job-type-checklist", "value"),
        Input("experience-level-checklist", "value"),
    ],
)
def update_avg_bar_chart(
    min_salary, max_salary, selected_job_types, selected_experience_levels
):
    # Start with the full DataFrame
    filtered_df = df.copy()

    # Apply salary filter
    filtered_df = filtered_df[
        (filtered_df["min_salary"] >= min_salary)
        & (filtered_df["max_salary"] <= max_salary)
    ]

    # Apply job type filter
    if selected_job_types:
        filtered_df = filtered_df[
            filtered_df["formatted_work_type"].isin(selected_job_types)
        ]

    # Apply experience level filter
    if selected_experience_levels:
        filtered_df = filtered_df[
            filtered_df["formatted_experience_level"].isin(selected_experience_levels)
        ]

    # Average Salary by Region updated
    filtered_df["avg_salary"] = filtered_df[["min_salary", "max_salary"]].mean(axis=1)
    avg_salary_by_region = (
        filtered_df.groupby("region")["avg_salary"].mean().reset_index()
    )
    avg_salary_by_region = avg_salary_by_region.sort_values(
        by="avg_salary", ascending=False
    )

    bar_colors_avg_sal = [
        region_colors[region] for region in avg_salary_by_region["region"]
    ]

    # New plot for average salary
    figure = go.Figure()
    figure.add_trace(
        go.Bar(
            x=avg_salary_by_region["region"],
            y=avg_salary_by_region["avg_salary"],
            marker=dict(color=bar_colors_avg_sal),
        )
    )
    figure.update_layout(
        title="Average Salary by Region",
        xaxis_title="Region",
        yaxis_title="Average Salary in USD",
        template="plotly_white",
    )

    return figure


@app.callback(
    Output("avg-min-max-salary-region", "figure"),
    [
        Input("min-salary-slider", "value"),
        Input("max-salary-slider", "value"),
        Input("job-type-checklist", "value"),
        Input("experience-level-checklist", "value"),
    ],
)
def update_min_max_bar_chart(
    min_salary, max_salary, selected_job_types, selected_experience_levels
):
    # Start with the full DataFrame
    filtered_df = df.copy()

    # Apply salary filter
    filtered_df = filtered_df[
        (filtered_df["min_salary"] >= min_salary)
        & (filtered_df["max_salary"] <= max_salary)
    ]

    # Apply job type filter
    if selected_job_types:
        filtered_df = filtered_df[
            filtered_df["formatted_work_type"].isin(selected_job_types)
        ]

    # Apply experience level filter
    if selected_experience_levels:
        filtered_df = filtered_df[
            filtered_df["formatted_experience_level"].isin(selected_experience_levels)
        ]

    avg_min_max_salaries_by_region = (
        filtered_df.groupby("region")
        .agg(
            avg_min_salary=("min_salary", "mean"), avg_max_salary=("max_salary", "mean")
        )
        .reset_index()
    )

    # Create a new figure
    figure = go.Figure(
        data=[
            go.Bar(
                name="Avg Min Salary",
                x=avg_min_max_salaries_by_region["region"],
                y=avg_min_max_salaries_by_region["avg_min_salary"],
            ),
            go.Bar(
                name="Avg Max Salary",
                x=avg_min_max_salaries_by_region["region"],
                y=avg_min_max_salaries_by_region["avg_max_salary"],
            ),
        ]
    )
    # Change the bar mode here if you prefer stacked bars
    figure.update_layout(
        barmode="group",
        title="Average Min and Max Salaries by Region",
        xaxis_title="Region",
        yaxis_title="Average Salary in USD",
    )

    return figure


@app.callback(
    Output('job-posting', 'figure'),
    [Input('state-dropdown', 'value')]
)
def update_graph(selected_states):
    df_filtered = df[(df['state_code'].isin(selected_states))]
    median_salary = df_filtered.groupby('state_code')['max_salary'].median().reset_index()

    fig = px.choropleth(median_salary, locations="state_code", color="max_salary",
                        locationmode="USA-states", scope="usa",
                        color_continuous_scale='Viridis',
                        range_color=(median_salary['max_salary'].min(), median_salary['max_salary'].max()),
                        labels={'max_salary': 'Median Max Salary'}, title='Median Max Salary by State')
    fig.update_layout(mapbox_style="carto-positron")

    return fig


# Run the app/dashboard
if __name__ == "__main__":
    app.run_server(debug=True)



