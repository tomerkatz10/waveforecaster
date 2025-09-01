#!/usr/bin/env python3
"""
Marine Weather Dashboard
Beautiful Streamlit dashboard for wave forecasting data
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import json
import os

from beaches import BEACH_OPTIONS, COMPARISON_BEACHES
from extract_info import MarineWeatherExtractor

# Page configuration
st.set_page_config(
    page_title="Tel Aviv Wave Forecasting",
    page_icon="🏄‍♂️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for beautiful styling with enhanced fonts and design
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600&display=swap');

.main-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 2.5rem;
    border-radius: 1.5rem;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}

.main-header h1 {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    font-size: 3.2rem;
    color: white;
    margin: 0;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    letter-spacing: -0.5px;
}

.main-header p {
    font-family: 'Inter', sans-serif;
    font-weight: 300;
    font-size: 1.3rem;
    color: rgba(255,255,255,0.95);
    margin: 0.8rem 0 0 0;
    letter-spacing: 0.5px;
}

    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.8rem;
        border-radius: 1.2rem;
        border-left: 5px solid #667eea;
        margin: 1.2rem 0;
        box-shadow: 0 6px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        color: #2c3e50;
    }
    
    .metric-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .metric-card h3 {
        font-family: 'Poppins', sans-serif;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 0.8rem;
        font-size: 1.4rem;
    }
    
    .metric-card p, .metric-card li {
        color: #2c3e50;
        font-family: 'Inter', sans-serif;
        font-size: 1rem;
        line-height: 1.6;
    }
    
    .metric-card ul {
        color: #2c3e50;
        margin: 0.5rem 0;
        padding-left: 1.5rem;
    }

.fetch-button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border: none;
    border-radius: 1rem;
    padding: 1rem 2.5rem;
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    font-size: 1.2rem;
    color: white;
    box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    transition: all 0.3s ease;
}

.fetch-button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.6);
}

.condition-good { color: #00d4aa; font-weight: 600; }
.condition-ok { color: #ff9500; font-weight: 600; }
.condition-bad { color: #ff3b30; font-weight: 600; }

.sidebar .sidebar-content {
    background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
}

.stButton > button {
    font-family: 'Poppins', sans-serif;
    font-weight: 500;
    border-radius: 0.8rem;
}

.stSelectbox > div > div {
    font-family: 'Inter', sans-serif;
}

.stSlider > div > div {
    font-family: 'Inter', sans-serif;
}

.stDateInput > div > div {
    font-family: 'Inter', sans-serif;
}

.stMarkdown {
    font-family: 'Inter', sans-serif;
}

.stInfo, .stSuccess, .stWarning {
    font-family: 'Inter', sans-serif;
    border-radius: 1rem;
}

.stSubheader {
    font-family: 'Poppins', sans-serif;
    font-weight: 600;
    color: #495057;
}

.stHeader {
    font-family: 'Poppins', sans-serif;
    font-weight: 700;
    color: #2c3e50;
}
</style>
""", unsafe_allow_html=True)



def create_wave_height_chart(data, selected_dates):
    """Create beautiful wave height trend chart"""
    if not data or 'processed_data' not in data:
        return go.Figure()
    
    # Prepare data for plotting
    plot_data = []
    for date, hourly_data in data['processed_data'].items():
        if date in selected_dates:
            for hour_data in hourly_data:
                plot_data.append({
                    'datetime': f"{date} {hour_data['hour']:02d}:00",
                    'wave_height': hour_data['wave_height'],
                    'swell_height': hour_data['swell_wave_height'],
                    'condition': hour_data['wave_condition']
                })
    
    if not plot_data:
        return go.Figure()
    
    df = pd.DataFrame(plot_data)
    df['datetime'] = pd.to_datetime(df['datetime'])
    
    # Create beautiful figure with enhanced styling
    fig = go.Figure()
    
    # Add wave height line with beautiful styling
    fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['wave_height'],
            mode='lines+markers',
            name='Wave Height',
            line=dict(
                color='#667eea',
                width=4,
                shape='spline',
                smoothing=1.3
            ),
            marker=dict(
                size=8,
                color='#667eea',
                line=dict(width=2, color='white'),
                symbol='circle',
                opacity=0.8
            ),
            fill='tonexty',
            fillcolor='rgba(102, 126, 234, 0.1)',
            hovertemplate='<b>%{x|%A, %B %d at %H:%M}</b><br>' +
                         'Wave Height: <b>%{y:.2f}m</b><extra></extra>'
        )
    )
    
    # Add swell height line with beautiful styling
    fig.add_trace(
        go.Scatter(
            x=df['datetime'],
            y=df['swell_height'],
            mode='lines+markers',
            name='Swell Height',
            line=dict(
                color='#764ba2',
                width=4,
                shape='spline',
                smoothing=1.3
            ),
            marker=dict(
                size=8,
                color='#764ba2',
                line=dict(width=2, color='white'),
                symbol='diamond',
                opacity=0.8
            ),
            hovertemplate='<b>%{x|%A, %B %d at %H:%M}</b><br>' +
                         'Swell Height: <b>%{y:.2f}m</b><extra></extra>'
        )
    )
    
    # Enhanced layout with beautiful design
    fig.update_layout(
        title={
            'text': '🌊 Wave Height Trends',
            'font': {'size': 26, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(255,255,255,0.98)',
        paper_bgcolor='rgba(255,255,255,0.98)',
        font={'family': 'Inter, sans-serif', 'color': '#2c3e50'},
        hovermode='x unified',
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1,
            'bgcolor': 'rgba(255,255,255,0.95)',
            'bordercolor': 'rgba(0,0,0,0.1)',
            'borderwidth': 1,
            'font': {'size': 14, 'color': '#2c3e50'},
            'itemsizing': 'constant'
        },
        margin=dict(l=70, r=70, t=90, b=70),
        height=550,
        showlegend=True
    )
    
    # Enhanced x-axis styling with day names
    fig.update_xaxes(
        title='Date & Time',
        title_font={'size': 16, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
        tickfont={'size': 13, 'color': '#2c3e50'},
        tickformat='%a %b %d',  # Shows day names like "Mon Sep 01"
        gridcolor='rgba(0,0,0,0.06)',
        gridwidth=1,
        showline=True,
        linewidth=2,
        linecolor='rgba(0,0,0,0.2)',
        zeroline=False,
        showgrid=True,
        tickangle=0
    )
    
    # Enhanced y-axis styling
    fig.update_yaxes(
        title='Height (meters)',
        title_font={'size': 16, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
        tickfont={'size': 13, 'color': '#2c3e50'},
        gridcolor='rgba(0,0,0,0.06)',
        gridwidth=1,
        showline=True,
        linewidth=2,
        linecolor='rgba(0,0,0,0.2)',
        zeroline=False,
        showgrid=True,
        rangemode='tozero'
    )
    
    return fig

def create_condition_heatmap(data, selected_dates):
    """Create hourly condition heatmap with simple, clear colors"""
    if not data or 'processed_data' not in data:
        return go.Figure()
    
    # Prepare data for heatmap
    heatmap_data = []
    dates = []
    hours = list(range(24))
    
    for date in selected_dates:
        if date in data['processed_data']:
            dates.append(date)
            daily_conditions = []
            hourly_data = data['processed_data'][date]
            
            for hour in range(24):
                hour_data = next((h for h in hourly_data if h['hour'] == hour), None)
                if hour_data:
                    # Use simple integer values for clearer color mapping
                    if hour_data['wave_condition'] == 'Good':
                        condition_value = 3
                    elif hour_data['wave_condition'] == 'OK':
                        condition_value = 2
                    elif hour_data['wave_condition'] == 'Bad':
                        condition_value = 1
                    else:
                        condition_value = 0
                    daily_conditions.append(condition_value)
                else:
                    daily_conditions.append(0)
            
            heatmap_data.append(daily_conditions)
    
    if not heatmap_data:
        return go.Figure()
    
    # Create heatmap with simple, clear colors
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=hours,
        y=dates,
        colorscale=[
            [0, '#f8f9fa'],      # Unknown - Light gray
            [0.33, '#ffb3b3'],   # Bad - Light red
            [0.66, '#fff2cc'],   # OK - Light yellow
            [1, '#c8e6c9']       # Good - Light green
        ],
        text=[[f"{'Unknown' if val == 0 else 'Bad' if val == 1 else 'OK' if val == 2 else 'Good'}" for val in row] for row in heatmap_data],
        texttemplate="%{text}",
        textfont={"size": 11, "color": "#2c3e50"},
        hoverongaps=False,
        hoverinfo='z+text'
    ))
    
    # Enhanced layout with beautiful design - theme-aware
    fig.update_layout(
        title={
            'text': '🌊 Hourly Wave Conditions',
            'font': {'size': 24, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(255,255,255,0.95)',
        paper_bgcolor='rgba(255,255,255,0.95)',
        font={'family': 'Inter, sans-serif', 'color': '#2c3e50'},
        height=500,
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    # Enhanced x-axis styling - theme-aware
    fig.update_xaxes(
        title='Hour of Day',
        title_font={'size': 16, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
        tickfont={'size': 12, 'color': '#2c3e50'},
        gridcolor='rgba(0,0,0,0.08)',
        gridwidth=1,
        showline=True,
        linewidth=1.5,
        linecolor='rgba(0,0,0,0.15)',
        zeroline=False,
        showgrid=True
    )
    
    # Enhanced y-axis styling - theme-aware
    fig.update_yaxes(
        title='Date',
        title_font={'size': 16, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
        tickfont={'size': 12, 'color': '#2c3e50'},
        gridwidth=1,
        showline=True,
        linewidth=1.5,
        linecolor='rgba(0,0,0,0.15)',
        zeroline=False,
        showgrid=True
    )
    
    return fig

def create_daily_summary_chart(data, selected_dates):
    """Create daily summary bar chart"""
    if not data or 'daily_summary' not in data:
        return go.Figure()
    
    # Filter data for selected dates
    filtered_summary = {date: summary for date, summary in data['daily_summary'].items() 
                       if date in selected_dates}
    
    if not filtered_summary:
        return go.Figure()
    
    dates = list(filtered_summary.keys())
    good_hours = [filtered_summary[date]['good_conditions_hours'] for date in dates]
    ok_hours = [filtered_summary[date]['ok_conditions_hours'] for date in dates]
    bad_hours = [filtered_summary[date]['bad_conditions_hours'] for date in dates]
    
    # Create stacked bar chart
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Good',
        x=dates,
        y=good_hours,
        marker_color='#2d5a27',  # Dark green for good conditions
        marker_line_color='white',
        marker_line_width=1
    ))
    
    fig.add_trace(go.Bar(
        name='OK',
        x=dates,
        y=ok_hours,
        marker_color='#a8e6cf',  # Light mint green for OK conditions
        marker_line_color='white',
        marker_line_width=1
    ))
    
    fig.add_trace(go.Bar(
        name='Bad',
        x=dates,
        y=bad_hours,
        marker_color='#ffb3b3',  # Light coral/pink
        marker_line_color='white',
        marker_line_width=1
    ))
    
    # Enhanced layout with beautiful design - theme-aware
    fig.update_layout(
        title={
            'text': '📊 Daily Wave Condition Summary',
            'font': {'size': 24, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        plot_bgcolor='rgba(255,255,255,0.95)',
        paper_bgcolor='rgba(255,255,255,0.95)',
        font={'family': 'Inter, sans-serif', 'color': '#2c3e50'},
        barmode='stack',
        height=500,
        margin=dict(l=60, r=60, t=80, b=60),
        legend={
            'orientation': 'h',
            'yanchor': 'bottom',
            'y': 1.02,
            'xanchor': 'right',
            'x': 1,
            'bgcolor': 'rgba(255,255,255,0.95)',
            'bordercolor': 'rgba(0,0,0,0.1)',
            'borderwidth': 1,
            'font': {'size': 12, 'color': '#2c3e50'}
        }
    )
    
    # Enhanced x-axis styling - theme-aware
    fig.update_xaxes(
        title='Date',
        title_font={'size': 16, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
        tickfont={'size': 12, 'color': '#2c3e50'},
        gridcolor='rgba(0,0,0,0.08)',
        gridwidth=1,
        showline=True,
        linewidth=1.5,
        linecolor='rgba(0,0,0,0.15)',
        zeroline=False,
        showgrid=True
    )
    
    # Enhanced y-axis styling - theme-aware
    fig.update_yaxes(
        title='Number of Hours',
        title_font={'size': 16, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
        tickfont={'size': 12, 'color': '#2c3e50'},
        gridcolor='rgba(0,0,0,0.08)',
        gridwidth=1,
        showline=True,
        linewidth=1.5,
        linecolor='rgba(0,0,0,0.15)',
        zeroline=False,
        showgrid=True
    )
    
    return fig

def create_wind_rose(data, selected_dates):
    """Create wind/wave direction rose chart"""
    if not data or 'processed_data' not in data:
        return go.Figure()
    
    # Prepare direction data
    directions = []
    for date in selected_dates:
        if date in data['processed_data']:
            for hour_data in data['processed_data'][date]:
                if hour_data['wave_direction'] is not None:
                    directions.append(hour_data['wave_direction'])
    
    if not directions:
        return go.Figure()
    
    # Create direction histogram
    fig = go.Figure()
    
    # Convert to 16-point compass
    compass_points = ['N', 'NNE', 'NE', 'ENE', 'E', 'ESE', 'SE', 'SSE',
                      'S', 'SSW', 'SW', 'WSW', 'W', 'WNW', 'NW', 'NNW']
    
    # Group directions into 16 bins
    bins = np.linspace(0, 360, 17)
    hist, bin_edges = np.histogram(directions, bins=bins)
    
    fig.add_trace(go.Barpolar(
        r=hist,
        theta=compass_points,
        name='Wave Direction',
        marker_color='#667eea',
        marker_line_color='white',
        marker_line_width=1,
        opacity=0.9
    ))
    
    # Enhanced layout with beautiful design - theme-aware
    fig.update_layout(
        title={
            'text': '🧭 Wave Direction Distribution',
            'font': {'size': 24, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
            'x': 0.5,
            'xanchor': 'center'
        },
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(hist) * 1.1],
                gridcolor='rgba(0,0,0,0.08)',
                gridwidth=1,
                linecolor='rgba(0,0,0,0.15)',
                linewidth=1.5
            ),
            angularaxis=dict(
                gridcolor='rgba(0,0,0,0.08)',
                gridwidth=1,
                linecolor='rgba(0,0,0,0.15)',
                linewidth=1.5
            ),
            bgcolor='rgba(255,255,255,0.95)'
        ),
        showlegend=False,
        height=500,
        plot_bgcolor='rgba(255,255,255,0.95)',
        paper_bgcolor='rgba(255,255,255,0.95)',
        font={'family': 'Inter, sans-serif', 'color': '#2c3e50'},
        margin=dict(l=60, r=60, t=80, b=60)
    )
    
    return fig

def main():
    """Main dashboard function"""
    
    # Auto-fetch data on page load/refresh
    if 'auto_fetch_initialized' not in st.session_state:
        st.session_state.auto_fetch_initialized = True
        st.session_state.fetch_data = True
        st.session_state.auto_fetch = True
    
    # Sidebar for controls
    with st.sidebar:
        st.header("⚙️ Dashboard Controls")
        
        # Beach selector
        st.subheader("🏖️ Beach Selection")
        beach_options = BEACH_OPTIONS
        
        selected_beach = st.selectbox(
            "Choose a Beach",
            options=list(beach_options.keys()),
            index=1,  # Default to Gordon Beach
            help="Select from popular Tel Aviv area beaches"
        )
        
        # Get coordinates for selected beach
        beach_coords = beach_options[selected_beach]
        lat = beach_coords["lat"]
        lon = beach_coords["lon"]
        beach_name = beach_coords["name"]
        
        # Check if beach selection changed
        if 'current_beach' in st.session_state and st.session_state.current_beach != beach_name:
            st.success(f"🏖️ Switched to {beach_name}! Click 'Fetch Latest Data' to get updated forecast.")
            # Clear previous data when beach changes
            if 'marine_data' in st.session_state:
                del st.session_state.marine_data
        

        
        # Custom location option
        if selected_beach == "Custom Location":
            st.subheader("📍 Custom Coordinates")
            lat = st.number_input("Latitude", value=32.08, format="%.2f", step=0.01, key="custom_lat")
            lon = st.number_input("Longitude", value=34.77, format="%.2f", step=0.01, key="custom_lon")
        
        # Forecast settings
        st.subheader("📅 Forecast Settings")
        forecast_days = st.slider("Forecast Days", min_value=1, max_value=7, value=7)

        
        # Date range selector
        st.subheader("📆 Date Range")
        today = datetime.now()
        end_date = today + timedelta(days=forecast_days)
        
        start_date = st.date_input("Start Date", value=today.date())
        end_date_input = st.date_input("End Date", value=end_date.date())
        
        # Store current parameters in session state
        st.session_state.current_lat = lat
        st.session_state.current_lon = lon
        st.session_state.current_beach = beach_name
        st.session_state.current_forecast_days = forecast_days
        st.session_state.current_start_date = start_date
        st.session_state.current_end_date = end_date_input
        
        # Parameter summary
        st.subheader("📋 Current Parameters")
        st.write(f"**Beach:** {beach_name}")
        st.write(f"**Date Range:** {start_date} to {end_date_input}")
        
        # Data control button
        if st.button("🔄 Refresh Parameters"):
            st.rerun()
        
        # Export options
        st.subheader("💾 Export Options")
        export_format = st.selectbox("Export Format", ["Excel", "JSON", "CSV"])
        
        if st.button("📥 Export Data"):
            st.session_state.export_data = True
    
    # Main content area - Fetch button at the top
    st.markdown("---")
    
    # Prominent fetch button at the top
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 **FETCH LATEST DATA**", type="primary", use_container_width=True):
            st.session_state.fetch_data = True
            # Clear previous data to force refresh
            if 'marine_data' in st.session_state:
                del st.session_state.marine_data
        st.caption("Click above to get the latest marine weather forecast")
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📊 Current Forecast Period")
        
        # Beautiful forecast info card
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1.5rem;
            border-radius: 1rem;
            color: white;
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
            margin: 1rem 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem; margin-right: 0.5rem;">🏖️</span>
                <h3 style="margin: 0; color: white; font-family: 'Poppins', sans-serif; font-weight: 600;">{beach_name}</h3>
            </div>
            <div style="font-size: 1.1rem; opacity: 0.95;">
                📅 Period: {start_date} to {end_date_input}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Status indicator
        if 'marine_data' in st.session_state:
            data_lat = st.session_state.marine_data['metadata']['latitude']
            data_lon = st.session_state.marine_data['metadata']['longitude']
            data_beach = st.session_state.marine_data['metadata'].get('beach_name', 'Unknown')
            
            if abs(data_lat - lat) > 0.001 or abs(data_lon - lon) > 0.001:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
                    padding: 1rem 1.5rem;
                    border-radius: 1rem;
                    color: white;
                    box-shadow: 0 6px 20px rgba(255, 152, 0, 0.3);
                    margin: 1rem 0;
                    text-align: center;
                    border: 2px solid rgba(255,255,255,0.2);
                ">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                        <span style="font-size: 1.3rem;">⚠️</span>
                        <span style="font-size: 1.1rem; font-weight: 600; font-family: 'Poppins', sans-serif;">
                            Data shown is for different coordinates. Fetch new data for current location.
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                <div style="
                    background: linear-gradient(135deg, #4caf50 0%, #45a049 100%);
                    padding: 1rem 1.5rem;
                    border-radius: 1rem;
                    color: white;
                    box-shadow: 0 6px 20px rgba(76, 175, 80, 0.3);
                    margin: 1rem 0;
                    text-align: center;
                    border: 2px solid rgba(255,255,255,0.2);
                ">
                    <div style="display: flex; align-items: center; justify-content: center; gap: 0.5rem;">
                        <span style="font-size: 1.3rem;">✅</span>
                        <span style="font-size: 1.1rem; font-weight: 600; font-family: 'Poppins', sans-serif;">
                            Data is current for selected location.
                        </span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Check if parameters have changed
        params_changed = (
            'current_lat' not in st.session_state or
            'current_lon' not in st.session_state or
            'current_beach' not in st.session_state or
            'current_forecast_days' not in st.session_state or
            st.session_state.get('current_lat') != lat or
            st.session_state.get('current_lon') != lon or
            st.session_state.get('current_beach') != beach_name or
            st.session_state.get('current_forecast_days') != forecast_days
        )
        
        if params_changed:
            st.info("🔄 Parameters changed! Click 'Fetch Latest Data' to update.")
        
        # Auto-fetch or manual fetch
        should_fetch = ('fetch_data' in st.session_state and st.session_state.fetch_data) or ('auto_fetch' in st.session_state and st.session_state.auto_fetch)
        
        if should_fetch:
            with st.spinner(f"Fetching marine weather data for {st.session_state.get('current_beach', beach_name)}..."):
                try:
                    # Use stored parameters for consistency
                    fetch_lat = st.session_state.get('current_lat', lat)
                    fetch_lon = st.session_state.get('current_lon', lon)
                    fetch_days = st.session_state.get('current_forecast_days', forecast_days)
                    
                    # Initialize extractor and fetch data
                    extractor = MarineWeatherExtractor(latitude=fetch_lat, longitude=fetch_lon)
                    raw_data = extractor.fetch_marine_data(length=fetch_days)
                    
                    if raw_data:
                        # Process the data
                        processed_data = extractor.process_wave_data(raw_data)
                        daily_summary = extractor.get_daily_summary(processed_data)
                        
                        # Prepare data for dashboard
                        data_to_save = {
                            'raw_data': raw_data,
                            'processed_data': processed_data,
                            'daily_summary': daily_summary,
                            'metadata': {
                                'latitude': fetch_lat,
                                'longitude': fetch_lon,
                                'beach_name': st.session_state.get('current_beach', beach_name),
                                'forecast_length': fetch_days,
                                'collection_timestamp': datetime.now().isoformat()
                            }
                        }
                        
                                                # Save to session state
                        st.session_state.marine_data = data_to_save
                        st.session_state.fetch_data = False
                        st.session_state.auto_fetch = False  # Clear auto-fetch after first load
                        
                        # Auto-export if requested
                        if 'export_data' in st.session_state and st.session_state.export_data:
                            if export_format == "Excel":
                                extractor.save_to_excel(data_to_save, "dashboard_export.xlsx")
                                st.success("📥 Data exported to Excel!")
                            elif export_format == "JSON":
                                extractor.save_to_file(data_to_save, "dashboard_export.json")
                                st.success("📥 Data exported to JSON!")
                            elif export_format == "CSV":
                                # Create CSV export
                                df = pd.DataFrame()
                                for date, hourly_data in processed_data.items():
                                    for hour_data in hourly_data:
                                        row = {
                                            'date': date,
                                            'hour': hour_data['hour'],
                                            'wave_height': hour_data['wave_height'],
                                            'wave_condition': hour_data['wave_condition'],
                                            'swell_height': hour_data['swell_wave_height'],
                                            'swell_period': hour_data['swell_wave_period']
                                        }
                                        df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
                                
                                df.to_csv("dashboard_export.csv", index=False)
                                st.success("📥 Data exported to CSV!")
                            
                            st.session_state.export_data = False
                    
                    else:
                        st.error("❌ Failed to fetch data. Please check your connection and try again.")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    # Display data if available
    if 'marine_data' in st.session_state:
        data = st.session_state.marine_data
        
        # Key metrics
        st.markdown("### 📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            total_hours = sum(len(hourly_data) for hourly_data in data['processed_data'].values())
            st.metric("Total Hours", total_hours)
        
        with col2:
            total_good = sum(summary['good_conditions_hours'] for summary in data['daily_summary'].values())
            st.metric("Good Conditions", total_good, delta=f"{total_good/total_hours*100:.1f}%")
        
        with col3:
            total_ok = sum(summary['ok_conditions_hours'] for summary in data['daily_summary'].values())
            st.metric("OK Conditions", total_ok, delta=f"{total_ok/total_hours*100:.1f}%")
        
        with col4:
            total_bad = sum(summary['bad_conditions_hours'] for summary in data['daily_summary'].values())
            st.metric("Bad Conditions", total_bad, delta=f"{total_bad/total_hours*100:.1f}%")
        
        # Get selected dates
        selected_dates = [date for date in data['processed_data'].keys() 
                         if datetime.strptime(date, '%Y-%m-%d').date() >= start_date 
                         and datetime.strptime(date, '%Y-%m-%d').date() <= end_date_input]
        
        # Charts
        st.markdown("### 📊 Wave Height Trends")
        wave_chart = create_wave_height_chart(data, selected_dates)
        st.plotly_chart(wave_chart, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🌊 Daily Condition Summary")
            daily_chart = create_daily_summary_chart(data, selected_dates)
            st.plotly_chart(daily_chart, use_container_width=True)
        
        with col2:
            st.markdown("### 🧭 Wave Direction")
            direction_chart = create_wind_rose(data, selected_dates)
            st.plotly_chart(direction_chart, use_container_width=True)
        
        st.markdown("### 🕐 Hourly Condition Heatmap")
        heatmap = create_condition_heatmap(data, selected_dates)
        st.plotly_chart(heatmap, use_container_width=True)
        
        # Beach comparison section
        st.markdown("### 🏖️ Beach Comparison")
        st.info("Compare wave conditions across different Tel Aviv beaches for a specific date")
        
        # Date selection for comparison
        col1, col2 = st.columns(2)
        with col1:
            comparison_date = st.date_input(
                "Select Date for Comparison",
                value=start_date,
                min_value=start_date,
                max_value=end_date_input,
                help="Choose a date to compare beach conditions"
            )
        
        with col2:
            # Use Streamlit button with custom CSS override for purple colors
            st.markdown("""
            <style>
            /* Target the specific button by its key */
            button[data-testid="baseButton-secondary"] {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                border-color: #667eea !important;
                color: white !important;
                font-weight: 500 !important;
                padding: 8px 16px !important;
                border-radius: 6px !important;
                min-width: 200px !important;
            }
            button[data-testid="baseButton-secondary"]:hover {
                background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%) !important;
                border-color: #5a6fd8 !important;
            }
            /* Alternative selectors to catch the button */
            .stButton > button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                border-color: #667eea !important;
                color: white !important;
            }
            </style>
            """, unsafe_allow_html=True)
            
            if st.button("🔄 Compare Beaches for Selected Date", key="compare-purple-button"):
                st.session_state.compare_beaches = True
        
        # Quick comparison of nearby beaches
        comparison_beaches = COMPARISON_BEACHES
        
        if 'compare_beaches' in st.session_state and st.session_state.compare_beaches:
            with st.spinner(f"Fetching comparison data for {comparison_date}..."):
                comparison_data = []
                best_surfing_times = {}
                
                for beach_name_comp, coords in comparison_beaches.items():
                    try:
                        extractor_comp = MarineWeatherExtractor(latitude=coords["lat"], longitude=coords["lon"])
                        raw_data_comp = extractor_comp.fetch_marine_data(length=7)  # 7 days for comparison
                        
                        if raw_data_comp:
                            processed_data_comp = extractor_comp.process_wave_data(raw_data_comp)
                            
                            # Get data for the specific comparison date
                            comparison_date_str = comparison_date.strftime('%Y-%m-%d')
                            if comparison_date_str in processed_data_comp:
                                daily_data = processed_data_comp[comparison_date_str]
                                
                                # Calculate wave and swell statistics for the day
                                wave_heights = [h['wave_height'] for h in daily_data if h['wave_height'] is not None]
                                swell_heights = [h['swell_wave_height'] for h in daily_data if h['swell_wave_height'] is not None]
                                swell_periods = [h['swell_wave_period'] for h in daily_data if h['swell_wave_period'] is not None]
                                
                                if wave_heights and swell_heights:
                                    # Find best surfing time (hour with best conditions)
                                    best_hour = None
                                    best_score = -1
                                    
                                    for hour_data in daily_data:
                                        if hour_data['wave_condition'] == 'Good':
                                            score = 3
                                        elif hour_data['wave_condition'] == 'OK':
                                            score = 2
                                        else:
                                            score = 1
                                        
                                        # Bonus for good swell period
                                        if hour_data['swell_wave_period'] and hour_data['swell_wave_period'] > 7:
                                            score += 0.5
                                        
                                        if score > best_score:
                                            best_score = score
                                            best_hour = hour_data['hour']
                                    
                                    best_time = f"{best_hour:02d}:00" if best_hour is not None else "N/A"
                                    
                                    # Calculate additional statistics for better comparison
                                    min_wave_height = np.min(wave_heights)
                                    wave_range = np.max(wave_heights) - min_wave_height
                                    good_conditions_count = sum(1 for h in daily_data if h['wave_condition'] == 'Good')
                                    ok_conditions_count = sum(1 for h in daily_data if h['wave_condition'] == 'OK')
                                    
                                    comparison_data.append({
                                        'Beach': beach_name_comp,
                                        'Min Wave (m)': f"{min_wave_height:.2f}",
                                        'Avg Wave (m)': f"{np.mean(wave_heights):.2f}",
                                        'Max Wave (m)': f"{np.max(wave_heights):.2f}",
                                        'Wave Range (m)': f"{wave_range:.2f}",
                                        'Avg Swell (m)': f"{np.mean(swell_heights):.2f}",
                                        'Max Swell (m)': f"{np.max(swell_heights):.2f}",
                                        'Avg Period (s)': f"{np.mean(swell_periods):.1f}",
                                        'Good Hours': good_conditions_count,
                                        'OK Hours': ok_conditions_count,
                                        'Best Time': best_time
                                    })
                                    
                                    best_surfing_times[beach_name_comp] = best_time
                    
                    except Exception as e:
                        st.warning(f"Could not fetch data for {beach_name_comp}: {str(e)}")
                
                if comparison_data:
                    # Display comparison table
                    st.markdown(f"#### 📊 Beach Comparison for {comparison_date.strftime('%A, %B %d, %Y')}")
                    comp_df = pd.DataFrame(comparison_data)
                    st.dataframe(comp_df, use_container_width=True)
                    
                    # Data quality and insights section
                    st.markdown("#### 📊 Data Insights & Quality")
                    
                    # Calculate overall statistics
                    all_wave_heights = []
                    all_swell_heights = []
                    all_swell_periods = []
                    
                    for row in comparison_data:
                        all_wave_heights.extend([float(row['Min Wave (m)']), float(row['Avg Wave (m)']), float(row['Max Wave (m)'])])
                        all_swell_heights.extend([float(row['Avg Swell (m)']), float(row['Max Swell (m)'])])
                        all_swell_periods.append(float(row['Avg Period (s)']))
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.metric(
                            "🌊 Overall Wave Range",
                            f"{max(all_wave_heights) - min(all_wave_heights):.2f}m",
                            help="Difference between highest and lowest wave heights across all beaches"
                        )
                    
                    with col2:
                        st.metric(
                            "🏖️ Beach Variation",
                            f"{np.std(all_wave_heights):.3f}m",
                            help="Standard deviation showing how much wave heights vary between beaches"
                        )
                    
                    with col3:
                        st.metric(
                            "⏰ Time Variation",
                            f"{np.mean([float(row['Wave Range (m)']) for row in comparison_data]):.3f}m",
                            help="Average daily wave height variation at each beach"
                        )
                    
                    # Data quality indicator
                    wave_variation = np.std(all_wave_heights)
                    if wave_variation < 0.05:
                        st.info("ℹ️ **Data Note:** Wave heights show very low variation across beaches and time. This is typical for calm Mediterranean conditions with consistent offshore winds.")
                    elif wave_variation < 0.15:
                        st.success("✅ **Good Variation:** Wave heights show moderate variation, indicating dynamic conditions.")
                    else:
                        st.warning("⚠️ **High Variation:** Wave heights show significant variation, indicating potentially challenging conditions.")
                    
                    # Debug information to verify data accuracy
                    with st.expander("🔍 Debug: Raw Data Verification"):
                        st.markdown("**Data Source Verification:**")
                        st.markdown(f"- **Selected Date:** {comparison_date.strftime('%Y-%m-%d')}")
                        st.markdown(f"- **API Units:** Wave height in meters, Swell height in meters, Period in seconds")
                        st.markdown(f"- **Data Points:** 24 hourly readings per beach")
                        st.markdown(f"- **Data Quality:** {'High' if wave_variation > 0.1 else 'Low variation (typical for calm conditions)'}")
                        
                        # Show sample raw data for first beach
                        if comparison_data:
                            first_beach = comparison_data[0]['Beach']
                            st.markdown(f"**Sample Data for {first_beach}:**")
                            
                            try:
                                extractor_sample = MarineWeatherExtractor(latitude=comparison_beaches[first_beach]["lat"], longitude=comparison_beaches[first_beach]["lon"])
                                raw_sample = extractor_sample.fetch_marine_data(length=7)
                                
                                if raw_sample:
                                    processed_sample = extractor_sample.process_wave_data(raw_sample)
                                    comparison_date_str = comparison_date.strftime('%Y-%m-%d')
                                    
                                    if comparison_date_str in processed_sample:
                                        sample_data = processed_sample[comparison_date_str]
                                        
                                        # Show first few hours
                                        sample_df = pd.DataFrame([
                                            {
                                                'Hour': f"{h['hour']:02d}:00",
                                                'Wave Height': f"{h['wave_height']:.3f}m" if h['wave_height'] else 'N/A',
                                                'Swell Height': f"{h['swell_wave_height']:.3f}m" if h['swell_wave_height'] else 'N/A',
                                                'Swell Period': f"{h['swell_wave_period']:.2f}s" if h['swell_wave_period'] else 'N/A',
                                                'Condition': h['wave_condition']
                                            }
                                            for h in sample_data[:6]  # First 6 hours
                                        ])
                                        
                                        st.dataframe(sample_df, use_container_width=True)
                                        
                                        # Show statistics
                                        wave_vals = [h['wave_height'] for h in sample_data if h['wave_height'] is not None]
                                        if wave_vals:
                                            st.markdown(f"**Wave Height Range:** {min(wave_vals):.3f}m - {max(wave_vals):.3f}m")
                                            st.markdown(f"**Average:** {np.mean(wave_vals):.3f}m")
                                            st.markdown(f"**Variation:** {np.std(wave_vals):.3f}m")
                                
                            except Exception as e:
                                st.warning(f"Could not fetch sample data: {str(e)}")
                    
                    # Create comprehensive wave height comparison chart
                    fig_wave = go.Figure()
                    
                    beaches = [row['Beach'] for row in comparison_data]
                    min_wave_heights = [float(row['Min Wave (m)']) for row in comparison_data]
                    avg_wave_heights = [float(row['Avg Wave (m)']) for row in comparison_data]
                    max_wave_heights = [float(row['Max Wave (m)']) for row in comparison_data]
                    
                    # Calculate y-axis range for better visualization
                    all_heights = min_wave_heights + avg_wave_heights + max_wave_heights
                    y_min = max(0, min(all_heights) - 0.1)  # Start from 0 or slightly below min
                    y_max = max(all_heights) + 0.1  # Add some padding above max
                    
                    # Add min, avg, and max wave heights with better colors
                    fig_wave.add_trace(go.Bar(
                        name='Min Wave Height',
                        x=beaches,
                        y=min_wave_heights,
                        marker_color='#74b9ff',
                        marker_line_color='white',
                        marker_line_width=1,
                        opacity=0.8,
                        hovertemplate='<b>%{x}</b><br>Min: %{y:.3f}m<extra></extra>'
                    ))
                    
                    fig_wave.add_trace(go.Bar(
                        name='Average Wave Height',
                        x=beaches,
                        y=avg_wave_heights,
                        marker_color='#667eea',
                        marker_line_color='white',
                        marker_line_width=1,
                        hovertemplate='<b>%{x}</b><br>Avg: %{y:.3f}m<extra></extra>'
                    ))
                    
                    fig_wave.add_trace(go.Bar(
                        name='Maximum Wave Height',
                        x=beaches,
                        y=max_wave_heights,
                        marker_color='#764ba2',
                        marker_line_color='white',
                        marker_line_width=1,
                        hovertemplate='<b>%{x}</b><br>Max: %{y:.3f}m<extra></extra>'
                    ))
                    
                    fig_wave.update_layout(
                        title={
                            'text': f'🌊 Wave Height Comparison - {comparison_date.strftime("%B %d")}',
                            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
                            'x': 0.5,
                            'xanchor': 'center'
                        },
                        xaxis_title="Beach",
                        yaxis_title="Height (meters)",
                        barmode='group',
                        height=500,
                        plot_bgcolor='rgba(255,255,255,0.95)',
                        paper_bgcolor='rgba(255,255,255,0.95)',
                        font={'family': 'Inter, sans-serif', 'color': '#2c3e50'},
                        legend={
                            'orientation': 'h',
                            'yanchor': 'bottom',
                            'y': 1.02,
                            'xanchor': 'right',
                            'x': 1,
                            'bgcolor': 'rgba(255,255,255,0.95)',
                            'bordercolor': 'rgba(0,0,0,0.2)',
                            'borderwidth': 1,
                            'font': {'size': 14, 'color': '#2c3e50', 'family': 'Inter, sans-serif'}
                        },
                        bargap=0.15,
                        bargroupgap=0.1,
                        yaxis=dict(
                            range=[y_min, y_max],
                            tickformat='.2f',
                            gridcolor='rgba(0,0,0,0.1)',
                            gridwidth=1
                        ),
                        xaxis=dict(
                            showline=True,
                            linecolor='#2c3e50',
                            linewidth=2,
                            showgrid=True,
                            gridcolor='rgba(0,0,0,0.1)',
                            gridwidth=1,
                            tickfont={'size': 12, 'color': '#2c3e50'},
                            title_font={'size': 14, 'color': '#2c3e50'}
                        )
                    )
                    
                    # Add data labels to the bars
                    fig_wave.update_traces(
                        texttemplate='%{y:.2f}m',
                        textposition='outside',
                        textfont={'size': 11, 'color': '#2c3e50'},
                        cliponaxis=False
                    )
                    
                    st.plotly_chart(fig_wave, use_container_width=True)
                    
                    # Create swell height comparison chart
                    fig_swell = go.Figure()
                    
                    avg_swell_heights = [float(row['Avg Swell (m)']) for row in comparison_data]
                    max_swell_heights = [float(row['Max Swell (m)']) for row in comparison_data]
                    avg_periods = [float(row['Avg Period (s)']) for row in comparison_data]
                    
                    # Add swell heights
                    fig_swell.add_trace(go.Bar(
                        name='Average Swell Height',
                        x=beaches,
                        y=avg_swell_heights,
                        marker_color='#00b894',
                        marker_line_color='white',
                        marker_line_width=1
                    ))
                    
                    fig_swell.add_trace(go.Bar(
                        name='Maximum Swell Height',
                        x=beaches,
                        y=max_swell_heights,
                        marker_color='#00a085',
                        marker_line_color='white',
                        marker_line_width=1
                    ))
                    
                    fig_swell.update_layout(
                        title={
                            'text': f'🌊 Swell Height Comparison - {comparison_date.strftime("%B %d")}',
                            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
                            'x': 0.5,
                            'xanchor': 'center'
                        },
                        xaxis_title="Beach",
                        yaxis_title="Height (meters)",
                        barmode='group',
                        height=450,
                        plot_bgcolor='rgba(255,255,255,0.95)',
                        paper_bgcolor='rgba(255,255,255,0.95)',
                        font={'family': 'Inter, sans-serif', 'color': '#2c3e50'},
                        legend={
                            'orientation': 'h',
                            'yanchor': 'bottom',
                            'y': 1.02,
                            'xanchor': 'right',
                            'x': 1,
                            'bgcolor': 'rgba(255,255,255,0.95)',
                            'bordercolor': 'rgba(0,0,0,0.2)',
                            'borderwidth': 1,
                            'font': {'size': 14, 'color': '#2c3e50', 'family': 'Inter, sans-serif'}
                        },
                        xaxis=dict(
                            showline=True,
                            linecolor='#2c3e50',
                            linewidth=2,
                            showgrid=True,
                            gridcolor='rgba(0,0,0,0.1)',
                            gridwidth=1,
                            tickfont={'size': 12, 'color': '#2c3e50'},
                            title_font={'size': 14, 'color': '#2c3e50'}
                        )
                    )
                    
                    # Add data labels to the swell bars
                    fig_swell.update_traces(
                        texttemplate='%{y:.2f}m',
                        textposition='outside',
                        textfont={'size': 11, 'color': '#2c3e50'},
                        cliponaxis=False
                    )
                    
                    st.plotly_chart(fig_swell, use_container_width=True)
                    
                    # Create swell period comparison chart
                    fig_period = go.Figure()
                    
                    fig_period.add_trace(go.Bar(
                        name='Average Swell Period',
                        x=beaches,
                        y=avg_periods,
                        marker_color='#fdcb6e',
                        marker_line_color='white',
                        marker_line_width=1
                    ))
                    
                    fig_period.update_layout(
                        title={
                            'text': f'⏱️ Swell Period Comparison - {comparison_date.strftime("%B %d")}',
                            'font': {'size': 20, 'color': '#2c3e50', 'family': 'Poppins, sans-serif'},
                            'x': 0.5,
                            'xanchor': 'center'
                        },
                        xaxis_title="Beach",
                        yaxis_title="Period (seconds)",
                        height=400,
                        plot_bgcolor='rgba(255,255,255,0.95)',
                        paper_bgcolor='rgba(255,255,255,0.95)',
                        font={'family': 'Inter, sans-serif', 'color': '#2c3e50'},
                        legend={
                            'bgcolor': 'rgba(255,255,255,0.95)',
                            'bordercolor': 'rgba(0,0,0,0.2)',
                            'borderwidth': 1,
                            'font': {'size': 14, 'color': '#2c3e50', 'family': 'Inter, sans-serif'}
                        },
                        xaxis=dict(
                            showline=True,
                            linecolor='#2c3e50',
                            linewidth=2,
                            showgrid=True,
                            gridcolor='rgba(0,0,0,0.1)',
                            gridwidth=1,
                            tickfont={'size': 12, 'color': '#2c3e50'},
                            title_font={'size': 14, 'color': '#2c3e50'}
                        )
                    )
                    
                    # Add data labels to the period bars
                    fig_period.update_traces(
                        texttemplate='%{y:.1f}s',
                        textposition='outside',
                        textfont={'size': 11, 'color': '#2c3e50'},
                        cliponaxis=False
                    )
                    
                    st.plotly_chart(fig_period, use_container_width=True)
                    
                    # Find best overall beach for the day
                    best_overall_beach = None
                    best_overall_score = -1
                    
                    for beach_data in comparison_data:
                        # Calculate overall score based on multiple factors
                        avg_wave = float(beach_data['Avg Wave (m)'])
                        max_wave = float(beach_data['Max Wave (m)'])
                        avg_swell = float(beach_data['Avg Swell (m)'])
                        avg_period = float(beach_data['Avg Period (s)'])
                        good_hours = int(beach_data['Good Hours'])
                        ok_hours = int(beach_data['OK Hours'])
                        
                        # Scoring system: wave height (0-3), swell quality (0-2), conditions (0-2)
                        wave_score = min(avg_wave * 2, 3)  # Cap at 3 points
                        swell_score = min(avg_swell * 1.5 + (avg_period - 5) * 0.1, 2)  # Cap at 2 points
                        condition_score = (good_hours * 2 + ok_hours * 1) / 24 * 2  # Cap at 2 points
                        
                        total_score = wave_score + swell_score + condition_score
                        
                        if total_score > best_overall_score:
                            best_overall_score = total_score
                            best_overall_beach = beach_data['Beach']
                    
                    # Display best beach summary
                    if best_overall_beach:
                        st.markdown("#### 🏆 Best Beach for the Day")
                        best_beach_data = next(row for row in comparison_data if row['Beach'] == best_overall_beach)
                        
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric(
                                "🏖️ Best Beach",
                                best_overall_beach,
                                help="Overall best beach based on wave height, swell quality, and conditions"
                            )
                        
                        with col2:
                            st.metric(
                                "🌊 Avg Wave Height",
                                f"{best_beach_data['Avg Wave (m)']}m",
                                help="Average wave height throughout the day"
                            )
                        
                        with col3:
                            st.metric(
                                "🌊 Avg Swell Height",
                                f"{best_beach_data['Avg Swell (m)']}m",
                                help="Average swell height throughout the day"
                            )
                        
                        with col4:
                            st.metric(
                                "⏱️ Best Time",
                                best_beach_data['Best Time'],
                                help="Optimal hour for surfing"
                            )
                    
                    # Best surfing times summary
                    st.markdown("#### 🏄‍♂️ Surfing Session Insights")
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        st.info("**🌅 Morning Session**\nCheck early hours for calmer conditions")
                    
                    with col2:
                        st.info("**☀️ Midday Session**\nOptimal conditions often during peak hours")
                    
                    with col3:
                        st.info("**🌆 Evening Session**\nLate afternoon can offer good waves")
                    
                    # Detailed hourly breakdown for each beach
                    st.markdown("#### 📋 Hourly Breakdown by Beach")
                    for beach_name_comp, coords in comparison_beaches.items():
                        if beach_name_comp in best_surfing_times:
                            with st.expander(f"🏖️ {beach_name_comp} - Hourly Details"):
                                try:
                                    extractor_comp = MarineWeatherExtractor(latitude=coords["lat"], longitude=coords["lon"])
                                    raw_data_comp = extractor_comp.fetch_marine_data(length=7)
                                    
                                    if raw_data_comp:
                                        processed_data_comp = extractor_comp.process_wave_data(raw_data_comp)
                                        comparison_date_str = comparison_date.strftime('%Y-%m-%d')
                                        
                                        if comparison_date_str in processed_data_comp:
                                            hourly_data = processed_data_comp[comparison_date_str]
                                            
                                            # Create hourly breakdown table
                                            hourly_table = []
                                            for hour_data in hourly_data:
                                                hourly_table.append({
                                                    'Hour': f"{hour_data['hour']:02d}:00",
                                                    'Wave Height (m)': f"{hour_data['wave_height']:.2f}" if hour_data['wave_height'] else 'N/A',
                                                    'Swell Height (m)': f"{hour_data['swell_wave_height']:.2f}" if hour_data['swell_wave_height'] else 'N/A',
                                                    'Swell Period (s)': f"{hour_data['swell_wave_period']:.1f}" if hour_data['swell_wave_period'] else 'N/A',
                                                    'Condition': hour_data['wave_condition']
                                                })
                                            
                                            hourly_df = pd.DataFrame(hourly_table)
                                            st.dataframe(hourly_df, use_container_width=True)
                                
                                except Exception as e:
                                    st.warning(f"Could not fetch hourly data for {beach_name_comp}")
                    
                    # Clear the comparison state
                    st.session_state.compare_beaches = False
                    
                else:
                    st.warning("No comparison data available for the selected date. Please try again.")
        
        # Detailed data table
        st.markdown("### 📋 Detailed Hourly Data")
        
        # Create detailed dataframe
        detailed_data = []
        for date in selected_dates:
            if date in data['processed_data']:
                for hour_data in data['processed_data'][date]:
                    detailed_data.append({
                        'Date': date,
                        'Hour': f"{hour_data['hour']:02d}:00",
                        'Wave Height (m)': f"{hour_data['wave_height']:.2f}" if hour_data['wave_height'] else 'N/A',
                        'Swell Height (m)': f"{hour_data['swell_wave_height']:.2f}" if hour_data['swell_wave_height'] else 'N/A',
                        'Swell Period (s)': f"{hour_data['swell_wave_period']:.1f}" if hour_data['swell_wave_period'] else 'N/A',
                        'Condition': hour_data['wave_condition']
                    })
        
        if detailed_data:
            df = pd.DataFrame(detailed_data)
            
            # Add color coding for conditions
            def color_condition(val):
                if val == 'Good':
                    return 'background-color: #00ff88; color: black'
                elif val == 'OK':
                    return 'background-color: #ffaa00; color: black'
                elif val == 'Bad':
                    return 'background-color: #ff4444; color: white'
                else:
                    return ''
            
            styled_df = df.style.applymap(color_condition, subset=['Condition'])
            st.dataframe(styled_df, use_container_width=True)
        
        # Best surfing times
        st.markdown("### 🏄‍♂️ Best Surfing Times")
        
        # Find best conditions
        best_times = []
        for date in selected_dates:
            if date in data['processed_data']:
                for hour_data in data['processed_data'][date]:
                    if hour_data['wave_condition'] == 'Good':
                        best_times.append({
                            'Date': date,
                            'Time': f"{hour_data['hour']:02d}:00",
                            'Wave Height': f"{hour_data['wave_height']:.2f}m",
                            'Swell Height': f"{hour_data['swell_wave_height']:.2f}m",
                            'Swell Period': f"{hour_data['swell_wave_period']:.1f}s"
                        })
        
        if best_times:
            best_df = pd.DataFrame(best_times)
            st.dataframe(best_df, use_container_width=True)
        else:
            st.info("No ideal surfing conditions found in the selected period. Consider OK conditions instead.")
    
    else:
        # Initial state
        st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 2rem;
            border-radius: 1.5rem;
            color: white;
            box-shadow: 0 15px 35px rgba(102, 126, 234, 0.3);
            margin: 2rem 0;
            border: 2px solid rgba(255,255,255,0.1);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -20px;
                right: -20px;
                width: 100px;
                height: 100px;
                background: rgba(255,255,255,0.1);
                border-radius: 50%;
                z-index: 1;
            "></div>
            <div style="position: relative; z-index: 2;">
                <h3 style="
                    margin: 0 0 1rem 0; 
                    color: white; 
                    font-family: 'Poppins', sans-serif; 
                    font-weight: 700; 
                    font-size: 1.8rem;
                    text-align: center;
                ">🚀 Get Started</h3>
                <p style="
                    text-align: center; 
                    margin-bottom: 1.5rem; 
                    font-size: 1.1rem; 
                    opacity: 0.9;
                    font-family: 'Inter', sans-serif;
                ">Use the sidebar controls to get started with your marine weather forecast</p>
                <div style="
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 1rem;
                    margin-top: 1.5rem;
                ">
                    <div style="
                        background: rgba(255,255,255,0.15);
                        padding: 1rem;
                        border-radius: 0.8rem;
                        text-align: center;
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🏖️</div>
                        <div style="font-size: 0.9rem; font-weight: 500;">Select Beach</div>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.15);
                        padding: 1rem;
                        border-radius: 0.8rem;
                        text-align: center;
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📅</div>
                        <div style="font-size: 0.9rem; font-weight: 500;">Set Period</div>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.15);
                        padding: 1rem;
                        border-radius: 0.8rem;
                        text-align: center;
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">🌊</div>
                        <div style="font-size: 0.9rem; font-weight: 500;">Fetch Data</div>
                    </div>
                    <div style="
                        background: rgba(255,255,255,0.15);
                        padding: 1rem;
                        border-radius: 0.8rem;
                        text-align: center;
                        border: 1px solid rgba(255,255,255,0.2);
                    ">
                        <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">📥</div>
                        <div style="font-size: 0.9rem; font-weight: 500;">Export</div>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Sample data preview
        st.markdown("### 📊 Sample Data Preview")
        st.info("Click 'Fetch Latest Data' to see real-time marine weather information!")
        
        # Forecast benefits
        st.markdown("### 🎯 Forecast Benefits")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.info("**📅 Weekly Planning**\nPlan your beach activities for the week ahead")
        
        with col2:
            st.info("**🌊 Pattern Recognition**\nIdentify daily and weekly wave patterns")
        
        with col3:
            st.info("**🏄‍♂️ Optimal Surfing**\nFind the best conditions for your sessions")
        
        # Beach information
        st.markdown("### 🏖️ Beach Information")
        beach_info = {
            "Gordon Beach": "Popular beach with good facilities, restaurants, and lifeguard services. Great for families and swimming.",
            "Frishman Beach": "Central location with beach volleyball courts and water sports. Popular with young crowds.",
            "Bograshov Beach": "Known for its relaxed atmosphere and good swimming conditions. Less crowded than Gordon.",
            "Jerusalem Beach": "Family-friendly beach with playground and good swimming areas. Popular with locals.",
            "Dolphinarium Beach": "Named after the old dolphinarium. Good for swimming and sunbathing.",
            "Maravi Beach": "Popular surfing spot with good wave conditions. Known for its surf culture.",
            "Hilton Beach": "Popular with surfers and water sports enthusiasts. Good wave conditions.",
            "Herzliya Beach": "Northern beach with marina and upscale atmosphere. Good for sailing and water sports.",
            "Bat Yam Beach": "Southern beach with good swimming conditions and family atmosphere.",
            "Holon Beach": "Southern location with good facilities and family-friendly environment."
        }
        
        if beach_name in beach_info:
            st.info(f"**{beach_name}**: {beach_info[beach_name]}")
        elif beach_name == "Custom":
            st.info("**Custom Location**: Enter your own coordinates for specific locations.")

if __name__ == "__main__":
    main()
