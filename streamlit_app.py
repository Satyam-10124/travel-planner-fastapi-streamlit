import streamlit as st
import requests
import pandas as pd
import folium
from streamlit_folium import st_folium
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, time
import asyncio
import httpx

# Page config
st.set_page_config(
    page_title="Travel Planner",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_BASE = "http://localhost:8000"

# Initialize session state
if 'trips' not in st.session_state:
    st.session_state.trips = []
if 'current_trip' not in st.session_state:
    st.session_state.current_trip = None

# Helper functions
def get_trips():
    """Fetch all trips from API"""
    try:
        response = requests.get(f"{API_BASE}/trips")
        if response.status_code == 200:
            return response.json()
        return []
    except requests.exceptions.ConnectionError:
        st.warning("⚠️ Backend not connected. Some features may not work.")
        return []
    except:
        return []

def create_trip_plan(plan_data):
    """Create a new trip plan"""
    try:
        response = requests.post(f"{API_BASE}/plan/generate", json=plan_data)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"API Error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to FastAPI backend. Make sure it's running on http://localhost:8000")
        return None
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        return None

def get_places(city=None, category=None):
    """Fetch places from API"""
    try:
        params = {}
        if city:
            params['city'] = city
        if category:
            params['category'] = category
        response = requests.get(f"{API_BASE}/places", params=params)
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

def get_recommendations(city):
    """Get recommendations for a city"""
    try:
        response = requests.get(f"{API_BASE}/Recommendations/{city}")
        if response.status_code == 200:
            return response.json()
        return []
    except:
        return []

# Sidebar Navigation
st.sidebar.title("🧳 Travel Planner")
page = st.sidebar.selectbox("Navigate", [
    "🏠 Home", 
    "✈️ Plan New Trip", 
    "📋 My Trips", 
    "🗺️ Explore Places", 
    "💰 Budget Tracker",
    "🌤️ Weather"
])

# Main content based on selected page
if page == "🏠 Home":
    st.title("Welcome to Travel Planner! ✈️")
    st.markdown("""
    ### Your AI-Powered Travel Companion
    
    Plan amazing trips with our intelligent travel planner that creates optimized itineraries based on your preferences.
    
    **Features:**
    - 🤖 AI-powered itinerary generation
    - 🗺️ Interactive maps with route optimization
    - 🌤️ Weather forecasts for your destination
    - 💰 Budget tracking and expense management
    - 📱 Real-time place recommendations
    """)
    
    # Quick stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Trips", len(get_trips()))
    
    with col2:
        st.metric("Places Available", len(get_places()))
    
    with col3:
        st.metric("Cities Covered", len(set([p.get('city', '') for p in get_places()])))
    
    # Recent trips
    st.subheader("Recent Trips")
    trips = get_trips()
    if trips:
        for trip in trips[-3:]:  # Show last 3 trips
            with st.expander(f"🎒 {trip['name']} - {trip['destination']}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Dates:** {trip['start_date']} to {trip['end_date']}")
                    st.write(f"**Travelers:** {trip['travelers']}")
                with col2:
                    if trip.get('budget'):
                        st.write(f"**Budget:** ${trip['budget']}")
                    if trip.get('notes'):
                        st.write(f"**Notes:** {trip['notes']}")
    else:
        st.info("No trips yet. Create your first trip using the 'Plan New Trip' page!")

elif page == "✈️ Plan New Trip":
    st.title("Plan Your Perfect Trip ✈️")
    
    with st.form("trip_planner"):
        col1, col2 = st.columns(2)
        
        with col1:
            destination = st.text_input("Destination (City or Country)", placeholder="e.g., Paris, Tokyo, New York, Japan, India")
            start_date = st.date_input("Start Date", value=date.today())
            end_date = st.date_input("End Date", value=date.today())
            trip_name = st.text_input("Trip Name", placeholder="e.g., Paris Adventure 2024")
            
        with col2:
            interests = st.multiselect(
                "Interests",
                ["sights", "museum", "food", "nature", "shopping", "nightlife", "activity"],
                default=["sights", "museum", "food"]
            )
            pace = st.selectbox("Travel Pace", ["relaxed", "standard", "packed"])
            budget_level = st.slider("Budget Level (0=Free, 4=Luxury)", 0, 4, 2)
            travelers = st.number_input("Number of Travelers", min_value=1, value=1)
        
        col3, col4 = st.columns(2)
        with col3:
            daily_start = st.time_input("Daily Start Time", value=time(9, 0))
            lunch_time = st.time_input("Lunch Time", value=time(13, 0))
        with col4:
            daily_end = st.time_input("Daily End Time", value=time(19, 0))
            origin = st.text_input("Origin City (optional)", placeholder="e.g., New York")

        dry_run = st.checkbox("Preview Only (don't save)", value=True)
        use_google = st.checkbox("Use Google Places (fetch fresh data)", value=False, help="Requires GOOGLE_PLACES_API_KEY in .env")
        country_mode = st.checkbox("Country Mode (spread across major areas)", value=False, help="Widens search radius; good for country inputs")
        
        submitted = st.form_submit_button("🚀 Generate Itinerary", type="primary")
        
        if submitted and destination:
            with st.spinner("Creating your perfect itinerary..."):
                plan_data = {
                    "destination": destination,
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "interests": interests,
                    "daily_start": daily_start.strftime("%H:%M:%S"),
                    "daily_end": daily_end.strftime("%H:%M:%S"),
                    "lunch_at": lunch_time.strftime("%H:%M:%S"),
                    "pace": pace,
                    "budget_level": budget_level,
                    "origin": origin,
                    "name": trip_name or f"{destination} Trip",
                    "travelers": travelers,
                    "dry_run": dry_run,
                    "use_google": use_google,
                    "country_mode": country_mode
                }
                
                result = create_trip_plan(plan_data)
                
                if result:
                    st.success("✅ Itinerary generated successfully!")
                    
                    if dry_run and 'preview' in result:
                        st.subheader("📅 Your Itinerary Preview")
                        preview_data = result['preview']
                        
                        # Create map
                        if preview_data['days']:
                            st.subheader("🗺️ Trip Map")
                            first_day_items = list(preview_data['days'].values())[0]
                            if first_day_items:
                                # Center map on first location
                                center_lat = first_day_items[0].get('lat', 48.8566)
                                center_lng = first_day_items[0].get('lng', 2.3522)
                                
                                m = folium.Map(location=[center_lat, center_lng], zoom_start=12)
                                
                                # Add markers for all locations
                                colors = ['red', 'blue', 'green', 'purple', 'orange', 'darkred', 'lightred']
                                day_idx = 0
                                
                                for day, items in preview_data['days'].items():
                                    color = colors[day_idx % len(colors)]
                                    for item in items:
                                        if item.get('lat') and item.get('lng'):
                                            folium.Marker(
                                                [item['lat'], item['lng']],
                                                popup=f"{item['title']}\n{item['start_time']} - {item['end_time']}",
                                                tooltip=item['title'],
                                                icon=folium.Icon(color=color)
                                            ).add_to(m)
                                    day_idx += 1
                                
                                st_folium(m, width=700, height=400)
                        
                        # Display daily schedule
                        for day, items in preview_data['days'].items():
                            st.subheader(f"📅 {day}")
                            
                            if items:
                                df = pd.DataFrame(items)
                                df = df[['start_time', 'end_time', 'title', 'type', 'location_name', 'notes']]
                                df.columns = ['Start', 'End', 'Activity', 'Type', 'Location', 'Notes']
                                st.dataframe(df, use_container_width=True)
                            else:
                                st.info("No activities planned for this day")
                    
                    elif not dry_run:
                        st.subheader("🎉 Trip Saved!")
                        trip_data = result.get('trip', {})
                        st.write(f"**Trip ID:** {trip_data.get('id')}")
                        st.write(f"**Name:** {trip_data.get('name')}")
                        st.write(f"**Destination:** {trip_data.get('destination')}")
                        
                        # Show itinerary items
                        items = result.get('items', [])
                        if items:
                            st.subheader("📋 Itinerary Items")
                            df = pd.DataFrame([item for item in items])
                            st.dataframe(df, use_container_width=True)
                
                else:
                    st.error("❌ Failed to generate itinerary. Please check your inputs and try again.")

elif page == "📋 My Trips":
    st.title("My Trips 🧳")
    
    trips = get_trips()
    
    if trips:
        # Trip selector
        trip_names = [f"{trip['name']} - {trip['destination']}" for trip in trips]
        selected_trip_idx = st.selectbox("Select a trip", range(len(trips)), format_func=lambda x: trip_names[x])
        
        if selected_trip_idx is not None:
            trip = trips[selected_trip_idx]
            
            # Trip details
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Destination", trip['destination'])
            with col2:
                st.metric("Duration", f"{trip['start_date']} to {trip['end_date']}")
            with col3:
                st.metric("Travelers", trip['travelers'])
            
            # Get trip plan
            try:
                response = requests.get(f"{API_BASE}/trips/{trip['id']}/plan")
                if response.status_code == 200:
                    plan_data = response.json()
                    
                    st.subheader("📅 Daily Itinerary")
                    
                    for day, items in plan_data.get('days', {}).items():
                        with st.expander(f"📅 {day} ({len(items)} activities)"):
                            if items:
                                for item in items:
                                    col1, col2, col3 = st.columns([2, 1, 3])
                                    with col1:
                                        st.write(f"**{item['title']}**")
                                        st.write(f"🕒 {item['start_time']} - {item['end_time']}")
                                    with col2:
                                        st.write(f"📍 {item['type']}")
                                    with col3:
                                        if item.get('notes'):
                                            st.write(item['notes'])
                                        if item.get('location_name'):
                                            st.write(f"📍 {item['location_name']}")
                            else:
                                st.info("No activities for this day")
                
            except:
                st.error("Failed to load trip details")
    
    else:
        st.info("No trips found. Create your first trip!")

elif page == "🗺️ Explore Places":
    st.title("Explore Places 🗺️")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Filters")
        city_filter = st.text_input("City", placeholder="e.g., Paris")
        category_filter = st.selectbox("Category", 
            ["All"] + ["sights", "museum", "food", "nature", "shopping", "nightlife", "activity"])
        
        if category_filter == "All":
            category_filter = None
        
        # Get places
        places = get_places(city_filter if city_filter else None, category_filter)
        
        st.subheader(f"Found {len(places)} places")
        
        # Display places list
        for place in places[:10]:  # Show first 10
            with st.expander(f"📍 {place['name']}"):
                st.write(f"**City:** {place['city']}")
                st.write(f"**Category:** {place['category']}")
                st.write(f"**Rating:** ⭐ {place['rating']}")
                st.write(f"**Price Level:** {'💰' * (place['price_level'] + 1)}")
                if place.get('description'):
                    st.write(f"**Description:** {place['description']}")
    
    with col2:
        st.subheader("Map View")
        
        if places:
            # Create map centered on first place
            center_lat = places[0]['lat']
            center_lng = places[0]['lng']
            
            m = folium.Map(location=[center_lat, center_lng], zoom_start=12)
            
            # Add markers for all places
            category_colors = {
                'sights': 'red',
                'museum': 'blue',
                'food': 'green',
                'nature': 'orange',
                'shopping': 'purple',
                'nightlife': 'darkred',
                'activity': 'lightblue'
            }
            
            for place in places:
                color = category_colors.get(place['category'], 'gray')
                folium.Marker(
                    [place['lat'], place['lng']],
                    popup=f"{place['name']}\n⭐ {place['rating']}\n{place['category']}",
                    tooltip=place['name'],
                    icon=folium.Icon(color=color)
                ).add_to(m)
            
            st_folium(m, width=700, height=500)
        else:
            st.info("No places to display. Try adjusting your filters.")

elif page == "💰 Budget Tracker":
    st.title("Budget Tracker 💰")
    
    # Sample budget data (in a real app, this would come from the database)
    st.subheader("Trip Expenses")
    
    # Budget planning
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Budget Planning")
        total_budget = st.number_input("Total Budget ($)", value=1000.0)
        
        # Budget categories
        categories = {
            "Accommodation": st.slider("Accommodation %", 0, 100, 40),
            "Food": st.slider("Food %", 0, 100, 25),
            "Transportation": st.slider("Transportation %", 0, 100, 15),
            "Activities": st.slider("Activities %", 0, 100, 15),
            "Shopping": st.slider("Shopping %", 0, 100, 5)
        }
        
        # Calculate amounts
        budget_breakdown = {}
        for category, percentage in categories.items():
            budget_breakdown[category] = (percentage / 100) * total_budget
    
    with col2:
        st.subheader("Budget Breakdown")
        
        # Create pie chart
        fig = px.pie(
            values=list(budget_breakdown.values()),
            names=list(budget_breakdown.keys()),
            title="Budget Allocation"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show breakdown table
        df = pd.DataFrame(list(budget_breakdown.items()), columns=['Category', 'Amount'])
        df['Amount'] = df['Amount'].apply(lambda x: f"${x:.2f}")
        st.dataframe(df, use_container_width=True)

elif page == "🌤️ Weather":
    st.title("Weather Forecast 🌤️")
    
    city = st.text_input("Enter city name", placeholder="e.g., Paris")
    
    if city:
        # Note: This would require actual weather API integration
        st.info("Weather integration requires API keys. Please add your OpenWeatherMap API key to the .env file.")
        
        # Mock weather data for demonstration
        st.subheader(f"Weather in {city}")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Temperature", "22°C", "2°C")
        with col2:
            st.metric("Humidity", "65%", "-5%")
        with col3:
            st.metric("Wind Speed", "15 km/h", "3 km/h")
        
        # 5-day forecast (mock data)
        st.subheader("5-Day Forecast")
        forecast_data = {
            'Day': ['Today', 'Tomorrow', 'Day 3', 'Day 4', 'Day 5'],
            'High': [22, 24, 21, 19, 23],
            'Low': [15, 17, 14, 12, 16],
            'Condition': ['Sunny', 'Partly Cloudy', 'Rainy', 'Cloudy', 'Sunny']
        }
        
        df = pd.DataFrame(forecast_data)
        st.dataframe(df, use_container_width=True)
        
        # Temperature chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['Day'], y=df['High'], mode='lines+markers', name='High', line=dict(color='red')))
        fig.add_trace(go.Scatter(x=df['Day'], y=df['Low'], mode='lines+markers', name='Low', line=dict(color='blue')))
        fig.update_layout(title='Temperature Forecast', xaxis_title='Day', yaxis_title='Temperature (°C)')
        st.plotly_chart(fig, use_container_width=True)

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ using Streamlit")
st.sidebar.markdown("🚀 Travel Planner v2.0")
