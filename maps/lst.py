import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Hanya memengaruhi konten, bukan elemen kontrol */
        .stMarkdown, .stText, .stTitle, .stHeader, .stSubheader, .stDataFrame {
            font-family: 'Poppins', sans-serif !important;
        }

        div[data-testid="stMarkdownContainer"] * {
            font-family: 'Poppins', sans-serif !important;
        }
    </style>
""", unsafe_allow_html=True)

# Get current subpage from session state
current_subpage = st.session_state.get('current_subpage', 'Maps')

# Page Title
st.title("🌡️ Land Surface Temperature (LST)")
st.write(f"**Current View:** {current_subpage}")

# Generate dummy data for demonstrations
@st.cache_data
def generate_dummy_data():
    # Generate sample coordinates for maps
    np.random.seed(42)
    lat = np.random.uniform(-6.3, -6.1, 100)  # Jakarta area
    lon = np.random.uniform(106.7, 106.9, 100)
    temperature = np.random.uniform(25, 45, 100)
    
    # Generate time series data
    dates = pd.date_range(start='2023-01-01', end='2023-12-31', freq='D')
    temp_series = 30 + 10 * np.sin(np.arange(len(dates)) * 2 * np.pi / 365) + np.random.normal(0, 2, len(dates))
    
    # Generate scatter plot data
    ndvi_values = np.random.uniform(0, 1, 100)
    lst_values = 45 - 15 * ndvi_values + np.random.normal(0, 3, 100)
    
    # Generate validation data
    observed = np.random.uniform(25, 45, 50)
    predicted = observed + np.random.normal(0, 2, 50)
    
    return {
        'map_data': pd.DataFrame({'lat': lat, 'lon': lon, 'temperature': temperature}),
        'time_series': pd.DataFrame({'date': dates, 'temperature': temp_series}),
        'scatter_data': pd.DataFrame({'ndvi': ndvi_values, 'lst': lst_values}),
        'validation_data': pd.DataFrame({'observed': observed, 'predicted': predicted})
    }

data = generate_dummy_data()

# Display content based on selected submenu
if current_subpage == "Maps":
    st.header("🗺️ LST Maps")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("Land Surface Temperature Distribution")
        
        # Create map visualization
        fig = px.scatter_mapbox(
            data['map_data'],
            lat="lat",
            lon="lon",
            color="temperature",
            size="temperature",
            hover_name="temperature",
            hover_data={"lat": True, "lon": True},
            color_continuous_scale="RdYlBu_r",
            size_max=15,
            zoom=10,
            title="LST Distribution Map"
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Statistics")
        st.metric("Max Temperature", f"{data['map_data']['temperature'].max():.1f}°C")
        st.metric("Min Temperature", f"{data['map_data']['temperature'].min():.1f}°C")
        st.metric("Avg Temperature", f"{data['map_data']['temperature'].mean():.1f}°C")
        st.metric("Data Points", len(data['map_data']))
        
        # Temperature ranges
        st.subheader("Temperature Ranges")
        hot = (data['map_data']['temperature'] > 35).sum()
        moderate = ((data['map_data']['temperature'] >= 30) & (data['map_data']['temperature'] <= 35)).sum()
        cool = (data['map_data']['temperature'] < 30).sum()
        
        st.write(f"🔥 Hot (>35°C): {hot} points")
        st.write(f"🌤️ Moderate (30-35°C): {moderate} points")
        st.write(f"❄️ Cool (<30°C): {cool} points")

elif current_subpage == "Graphic":
    st.header("📊 LST Graphics")
    
    tab1, tab2, tab3 = st.tabs(["Time Series", "Distribution", "Heatmap"])
    
    with tab1:
        st.subheader("Temperature Time Series")
        fig = px.line(
            data['time_series'],
            x='date',
            y='temperature',
            title='Daily Land Surface Temperature Variation',
            labels={'temperature': 'Temperature (°C)', 'date': 'Date'}
        )
        fig.add_hline(y=data['time_series']['temperature'].mean(), 
                     line_dash="dash", 
                     annotation_text="Average Temperature")
        st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("Temperature Distribution")
        fig = px.histogram(
            data['map_data'],
            x='temperature',
            nbins=20,
            title='LST Distribution',
            labels={'temperature': 'Temperature (°C)', 'count': 'Frequency'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader("Monthly Temperature Heatmap")
        # Create dummy monthly data
        monthly_data = data['time_series'].copy()
        monthly_data['month'] = monthly_data['date'].dt.month
        monthly_data['day'] = monthly_data['date'].dt.day
        
        # Create pivot table for heatmap
        heatmap_data = monthly_data.pivot_table(
            values='temperature',
            index='month',
            columns='day',
            aggfunc='mean'
        )
        
        fig = px.imshow(
            heatmap_data,
            title='Monthly Temperature Heatmap',
            labels=dict(x="Day of Month", y="Month", color="Temperature (°C)"),
            color_continuous_scale="RdYlBu_r"
        )
        st.plotly_chart(fig, use_container_width=True)

elif current_subpage == "Scatter Plot":
    st.header("📈 LST Scatter Plot Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.subheader("LST vs NDVI Relationship")
        
        # Create scatter plot
        fig = px.scatter(
            data['scatter_data'],
            x='ndvi',
            y='lst',
            title='Land Surface Temperature vs NDVI',
            labels={'ndvi': 'NDVI', 'lst': 'LST (°C)'},
            trendline="ols"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Show correlation
        correlation = data['scatter_data']['ndvi'].corr(data['scatter_data']['lst'])
        st.info(f"Correlation coefficient: {correlation:.3f}")
    
    with col2:
        st.subheader("Analysis Controls")
        
        # Add some interactive controls
        show_trendline = st.checkbox("Show Trendline", value=True)
        color_by = st.selectbox("Color by:", ["None", "LST Range", "NDVI Range"])
        
        if color_by == "LST Range":
            data['scatter_data']['lst_category'] = pd.cut(
                data['scatter_data']['lst'],
                bins=3,
                labels=['Low', 'Medium', 'High']
            )
        elif color_by == "NDVI Range":
            data['scatter_data']['ndvi_category'] = pd.cut(
                data['scatter_data']['ndvi'],
                bins=3,
                labels=['Low', 'Medium', 'High']
            )
        
        st.subheader("Statistics")
        st.write(f"R² Score: {correlation**2:.3f}")
        st.write(f"Sample Size: {len(data['scatter_data'])}")
        
        # Show regression equation
        from sklearn.linear_model import LinearRegression
        X = data['scatter_data']['ndvi'].values.reshape(-1, 1)
        y = data['scatter_data']['lst'].values
        reg = LinearRegression().fit(X, y)
        st.write(f"Equation: LST = {reg.coef_[0]:.2f} × NDVI + {reg.intercept_:.2f}")

elif current_subpage == "Validate":
    st.header("✅ LST Validation")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Observed vs Predicted Values")
        
        # Create validation scatter plot
        fig = px.scatter(
            data['validation_data'],
            x='observed',
            y='predicted',
            title='LST Validation: Observed vs Predicted',
            labels={'observed': 'Observed LST (°C)', 'predicted': 'Predicted LST (°C)'}
        )
        
        # Add perfect prediction line
        min_val = min(data['validation_data']['observed'].min(), data['validation_data']['predicted'].min())
        max_val = max(data['validation_data']['observed'].max(), data['validation_data']['predicted'].max())
        fig.add_trace(go.Scatter(
            x=[min_val, max_val],
            y=[min_val, max_val],
            mode='lines',
            name='Perfect Prediction',
            line=dict(dash='dash', color='red')
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Validation Metrics")
        
        # Calculate validation metrics
        from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
        
        observed = data['validation_data']['observed']
        predicted = data['validation_data']['predicted']
        
        rmse = np.sqrt(mean_squared_error(observed, predicted))
        mae = mean_absolute_error(observed, predicted)
        r2 = r2_score(observed, predicted)
        bias = np.mean(predicted - observed)
        
        st.metric("RMSE", f"{rmse:.2f}°C")
        st.metric("MAE", f"{mae:.2f}°C")
        st.metric("R² Score", f"{r2:.3f}")
        st.metric("Bias", f"{bias:.2f}°C")
        
        # Residual analysis
        residuals = predicted - observed
        st.subheader("Residual Analysis")
        fig_res = px.histogram(
            x=residuals,
            nbins=15,
            title='Residual Distribution',
            labels={'x': 'Residuals (°C)', 'y': 'Frequency'}
        )
        st.plotly_chart(fig_res, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("*This is a demo page showing LST analysis capabilities.*")