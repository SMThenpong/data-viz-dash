from dash import Dash, html, dcc, callback, Output, Input
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
import requests

# Incorporate data
airbnb_data_url = 'https://raw.githubusercontent.com/Luodina/js-data-viz/3rd-stage/step-4-render-neighbourhood-chart/data/airbnb-data.json'
response = requests.get(airbnb_data_url)
accommodations = response.json()

type_of_accommodation = {
    'Private room': 0,
    'Entire home/apt': 0,
    'Shared room': 0
}

for accommodation in accommodations:
    room_type = accommodation.get('room_type')
    if room_type in type_of_accommodation:
        type_of_accommodation[room_type] += 1

accommodation_df = pd.DataFrame.from_dict(
    {'Type': list(type_of_accommodation.keys()),
     'Count': list(type_of_accommodation.values())}
)

accommodation_price = {
    'Less than 500': 0,
    'Less than 1000': 0,
    'Less than 2000': 0,
    'Less than 4000': 0,
    'More than 3999': 0
}

for accommodation in accommodations:
    price = accommodation.get('price', 0)
    if price < 500:
        accommodation_price['Less than 500'] += 1
    elif price < 1000:
        accommodation_price['Less than 1000'] += 1
    elif price < 2000:
        accommodation_price['Less than 2000'] += 1
    elif price < 4000:
        accommodation_price['Less than 4000'] += 1
    else:
        accommodation_price['More than 3999'] += 1

# Pie chart
price_df = pd.DataFrame.from_dict(
    {'Price Category': list(accommodation_price.keys()),
     'Count': list(accommodation_price.values())}
)

neighbourhoods = {}
for accommodation in accommodations:
    room_type = accommodation.get('room_type')
    neighbourhood = accommodation.get('neighbourhood')
    
    if room_type not in neighbourhoods:
        neighbourhoods[room_type] = {}
    
    if neighbourhood not in neighbourhoods[room_type]:
        neighbourhoods[room_type][neighbourhood] = 0
    
    neighbourhoods[room_type][neighbourhood] += 1

# Area chart for neighbourhood
neighbourhood_labels = sorted(set(neighbourhoods['Private room'].keys()).union(neighbourhoods['Entire home/apt'].keys()).union(neighbourhoods['Shared room'].keys()))
private_rooms = [neighbourhoods['Private room'].get(n, 0) for n in neighbourhood_labels]
entire_home = [neighbourhoods['Entire home/apt'].get(n, 0) for n in neighbourhood_labels]
shared_rooms = [neighbourhoods['Shared room'].get(n, 0) for n in neighbourhood_labels]

# Initialize the app
app = Dash()


# App layout
app.layout = dbc.Container([
    dbc.Row([
        html.Div('Exploratory Data Visualization of Airbnb Dataset', className="text-primary text-center fs-3")
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='types-of-accommodation-chart')
        ], width=6),

        dbc.Col([
            dcc.Graph(figure={}, id='accommodation-price-chart')
        ], width=6),
    ]),

    dbc.Row([
        dbc.Col([
            dcc.Graph(figure={}, id='neighbourhood-chart')
        ], width=12),
    ]),
], fluid=True)


@callback(
    Output(component_id='types-of-accommodation-chart', component_property='figure'),
    Input(component_id='types-of-accommodation-chart', component_property='id')  # Dummy input to trigger the graph update
)
def type_of_accommodation_bar_chart(_):
    fig = px.bar(
        accommodation_df,
        x='Type',
        y='Count',
        title='Types of Accommodation',
        labels={'Count': 'Number of Listings'}
    )
    return fig

@callback(
    Output(component_id='accommodation-price-chart', component_property='figure'),
    Input(component_id='accommodation-price-chart', component_property='id')
)
def accommodation_price_pie_chart(_):
    fig = px.pie(
        price_df,
        names='Price Category',
        values='Count',
        title='Accommodation Price Distribution',
        hole=0.4
    )
    return fig

@callback(
    Output(component_id='neighbourhood-chart', component_property='figure'),
    Input(component_id='neighbourhood-chart', component_property='id') 
)
def neighbourhood_area_chart(_):
    fig = px.area(
        x=neighbourhood_labels,
        y=[private_rooms, entire_home, shared_rooms],
        title='Neighbourhood Listings by Room Type',
        labels={'x': 'Neighbourhood', 'y': 'Number of Listings'},
        template='plotly'
    )
    fig.add_scatter(x=neighbourhood_labels, y=private_rooms, mode='lines', name='Private room')
    fig.add_scatter(x=neighbourhood_labels, y=entire_home, mode='lines', name='Entire home/apt')
    fig.add_scatter(x=neighbourhood_labels, y=shared_rooms, mode='lines', name='Shared room')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
