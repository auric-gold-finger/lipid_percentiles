import streamlit as st
import plotly.graph_objects as go
import numpy as np
import pandas as pd

st.set_page_config(page_title="Lipid Profile Percentile Visualizer", layout="wide")

# Enhanced CSS for better visual appearance - just title styling, no cards
st.markdown("""
<style>
    .main {
        padding-top: 1rem;
    }
    h1, h2, h3 {
        color: #2c3e50;
    }
    .stMetric {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 5px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24);
    }
    .chart-title {
        font-family: 'Cormorant Garamond', serif;
        font-size: 2em;
        font-weight: bold;
        color: #2c3e50;
        margin-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)

st.title("Lipid Profile Percentile Visualizer")

# Function to get correct ordinal suffix
def get_ordinal_suffix(num):
    """Return the correct ordinal suffix for a number (st, nd, rd, th)"""
    num = int(round(num))  # Ensure we're working with an integer
    if 11 <= (num % 100) <= 13:
        return 'th'
    else:
        remainder = num % 10
        if remainder == 1:
            return 'st'
        elif remainder == 2:
            return 'nd'
        elif remainder == 3:
            return 'rd'
        else:
            return 'th'

# Data from the provided tables
percentiles = [1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99]
apoB_values = [41, 54, 61, 70, 77, 84, 90, 97, 104, 113, 125, 137, 160]
nonHDL_values = [59, 79, 88, 103, 114, 125, 135, 145, 156, 170, 191, 208, 247]
LDL_values = [45, 63, 72, 85, 95, 104, 112, 121, 131, 143, 161, 176, 211]

# Lp(a) data - different percentiles from the other lipids
lpa_percentiles = [75, 80, 90, 95, 98, 99]
lpa_values = [47, 60, 90, 116, 180, 245]

# Common display percentiles for standard lipids
std_key_percentiles = [0, 5, 10, 20, 50, 75, 100]

# Specialized display percentiles for Lp(a)
lpa_key_percentiles = [0, 75, 80, 90, 95, 98, 99, 100]

# Create a sidebar for inputs with improved styling
st.sidebar.header("Patient Lipid Values")

# Input fields with better ranges and defaults
apoB = st.sidebar.number_input("ApoB (mg/dL)", min_value=20, max_value=200, value=90, 
                               help="Normal range typically 60-120 mg/dL")
nonHDL = st.sidebar.number_input("Non-HDL-C (mg/dL)", min_value=40, max_value=250, value=135, 
                                help="Goal typically <130 mg/dL for most adults")
LDL = st.sidebar.number_input("LDL-C (mg/dL)", min_value=30, max_value=230, value=112, 
                             help="Goal typically <100 mg/dL for most adults")
lpa = st.sidebar.number_input("Lp(a) (mg/dL)", min_value=0, max_value=250, value=30, 
                             help="Values >50 mg/dL may indicate increased cardiovascular risk")

# Function to determine percentile based on value
def get_percentile(value, perc_array, value_array):
    if value <= value_array[0]:
        return perc_array[0]
    if value >= value_array[-1]:
        return perc_array[-1]
    return np.interp(value, value_array, perc_array)

# Calculate percentiles for patient values
apoB_percentile = get_percentile(apoB, percentiles, apoB_values)
nonHDL_percentile = get_percentile(nonHDL, percentiles, nonHDL_values)
LDL_percentile = get_percentile(LDL, percentiles, LDL_values)
lpa_percentile = get_percentile(lpa, lpa_values, lpa_percentiles)  # Note reversed order for Lp(a)

# Determine risk level
def get_risk_level(percentile, marker="lipid"):
    if marker == "lpa":
        if percentile < 75:
            return "Low Risk", "normal"
        elif percentile < 90:
            return "Moderate Risk", "off"
        else:
            return "High Risk", "inverse"
    else:
        if percentile <= 20:
            return "Low Risk", "normal"
        elif percentile < 50:
            return "Moderate Risk", "off"
        else:
            return "High Risk", "inverse"

# Ensure correct ordinal suffixes for metric display
apoB_percentile_int = int(round(apoB_percentile))
apoB_suffix = get_ordinal_suffix(apoB_percentile_int)

nonHDL_percentile_int = int(round(nonHDL_percentile))
nonHDL_suffix = get_ordinal_suffix(nonHDL_percentile_int)

LDL_percentile_int = int(round(LDL_percentile))
LDL_suffix = get_ordinal_suffix(LDL_percentile_int)

lpa_percentile_int = int(round(lpa_percentile))
lpa_suffix = get_ordinal_suffix(lpa_percentile_int)

# Display patient metrics in cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    risk_text, risk_color = get_risk_level(apoB_percentile)
    st.metric("ApoB Percentile", f"{apoB_percentile_int}{apoB_suffix}", 
              delta=risk_text, delta_color=risk_color)
with col2:
    risk_text, risk_color = get_risk_level(nonHDL_percentile)
    st.metric("Non-HDL-C Percentile", f"{nonHDL_percentile_int}{nonHDL_suffix}", 
              delta=risk_text, delta_color=risk_color)
with col3:
    risk_text, risk_color = get_risk_level(LDL_percentile)
    st.metric("LDL-C Percentile", f"{LDL_percentile_int}{LDL_suffix}", 
              delta=risk_text, delta_color=risk_color)
with col4:
    risk_text, risk_color = get_risk_level(lpa_percentile, "lpa")
    st.metric("Lp(a) Percentile", f"{lpa_percentile_int}{lpa_suffix}", 
              delta=risk_text, delta_color=risk_color)

# Function to create a standard lipid percentile chart
def create_standard_chart(title, percentiles, values, patient_value, key_percentiles=std_key_percentiles):
    # Get key values for the specified percentiles (interpolate if needed)
    key_values = np.interp(key_percentiles, [min(1, min(percentiles)), *percentiles, max(99, max(percentiles))], 
                          [np.interp(1, percentiles, values), *values, np.interp(99, percentiles, values)])
    
    # Calculate patient percentile
    patient_percentile = get_percentile(patient_value, percentiles, values)
    
    # Determine risk level text for the annotation
    if patient_percentile <= 20:
        risk_text = "Low Risk"
    elif patient_percentile < 50:
        risk_text = "Moderate Risk"
    else:
        risk_text = "High Risk"
    
    # Create figure
    fig = go.Figure()
    
    # Define x-axis as percentiles (normalized) from 0-100
    x_range = [0, 100]  # All charts will have the same x-range
    
    # Add a range slider background (full length)
    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 0],
        mode='lines',
        line=dict(
            color='lightgrey',
            width=10,
        ),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Standard colorscale for lipids
    colorscale = [
        [0, 'rgba(50, 200, 50, 1)'],      # Green
        [0.1, 'rgba(150, 200, 50, 1)'],    # Light green
        [0.2, 'rgba(220, 220, 50, 1)'],   # Yellow
        [0.35, 'rgba(230, 180, 50, 1)'],    # Light orange
        [0.5, 'rgba(230, 130, 50, 1)'],    # Orange
        [0.75, 'rgba(230, 90, 50, 1)'],    # Dark orange
        [0.85, 'rgba(220, 50, 50, 1)']        # Red
    ]
    
    # Add colored segments based on percentiles
    for i in range(len(key_percentiles) - 1):
        # Get the actual percentile values
        start_percentile = key_percentiles[i]
        end_percentile = key_percentiles[i+1]
        
        # Normalize percentile position for color selection
        color_pos = start_percentile / 100
        
        # Find color from scale
        color = interpolate_color(colorscale, color_pos)
        
        # Add segment
        fig.add_trace(go.Scatter(
            x=[start_percentile, end_percentile],
            y=[0, 0],
            mode='lines',
            line=dict(
                color=color,
                width=20,
            ),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Add marker lines and labels for key percentiles
    # Skip the 0 and 100 percentiles for labels as they're at the edges
    display_percentiles = key_percentiles[1:-1] if len(key_percentiles) > 2 else key_percentiles
    display_values = key_values[1:-1] if len(key_values) > 2 else key_values
    
    for i, (perc, val) in enumerate(zip(display_percentiles, display_values)):
        # Get correct ordinal suffix - ensure we're using integers
        perc_int = int(round(perc))
        suffix = get_ordinal_suffix(perc_int)
        
        # Add percentile label below
        fig.add_annotation(
            x=perc,
            y=-0.8,
            text=f"{perc_int}<sup>{suffix}</sup>",
            showarrow=False,
            font=dict(size=18, color="#333333", family="Cormorant Garamond"),
        )
        
        # Add value label above with transparent background
        fig.add_annotation(
            x=perc,
            y=0.7,
            text=f"{int(round(val))}",
            showarrow=False,
            font=dict(size=16, color="#000000", family="Avenir"),
            bgcolor="rgba(255,255,255,0.0)",
            borderpad=4,
        )
    
    # Add a vertical line for the patient marker
    fig.add_shape(
        type="line",
        x0=patient_percentile,
        x1=patient_percentile,
        y0=-0.4,
        y1=0.4,
        line=dict(
            color="#000000",
            width=4,
            dash="solid"
        )
    )
    
    # Add a highlight effect at the top and bottom of the line
    fig.add_trace(go.Scatter(
        x=[patient_percentile],
        y=[0.4],
        mode="markers",
        marker=dict(
            size=12,
            symbol="triangle-down",
            color="#000000",
            line=dict(width=2, color="white")
        ),
        showlegend=False,
        hoverinfo="none"
    ))
    
    fig.add_trace(go.Scatter(
        x=[patient_percentile],
        y=[-0.4],
        mode="markers",
        marker=dict(
            size=12,
            symbol="triangle-up",
            color="#000000",
            line=dict(width=2, color="white")
        ),
        name="Patient",
        hovertemplate=f"Patient: {patient_value} mg/dL<br>Percentile: {int(round(patient_percentile))}{get_ordinal_suffix(int(round(patient_percentile)))}"
    ))
    
    # Check if patient percentile is not at a key percentile (with some tolerance)
    tolerance = 4.0  # Allow 4 percentile points of tolerance
    is_at_key_percentile = any(abs(patient_percentile - p) < tolerance for p in display_percentiles)
    
    # Only add annotations if NOT at a key percentile
    if not is_at_key_percentile:
        # Add patient value annotation (above the line)
        fig.add_annotation(
            x=patient_percentile,
            y=0.7,
            text=f"{patient_value}",
            showarrow=False,  # No arrow
            font=dict(size=16, color="#000000", family="Avenir"),
            bgcolor="rgba(255,255,255,0.0)",  # Transparent background
            borderpad=4,
        )
        
        # Get correct ordinal suffix for patient percentile - ensure we're using an integer
        patient_percentile_int = int(round(patient_percentile))
        suffix = get_ordinal_suffix(patient_percentile_int)
        
        # Add percentile annotation (below the line)
        fig.add_annotation(
            x=patient_percentile,
            y=-0.8,
            text=f"{patient_percentile_int}<sup>{suffix}</sup>",
            showarrow=False,  # No arrow
            font=dict(size=18, color="#000000", family="cormorant garamond"),
            bgcolor="rgba(255,255,255,0.0)",  # Transparent background
            borderpad=4,
        )
    
    # Update layout for a cleaner look
    fig.update_layout(
        height=180,
        margin=dict(l=40, r=40, t=20, b=60),
        xaxis=dict(
            range=[-5, 105],  # Consistent range for all charts
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            range=[-0.8, 0.8],
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            fixedrange=True
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hovermode="closest"
    )
    
    return fig

# Function to create an Lp(a) specific chart - handles the inverted percentile/value relationship
# Change the following function in your code to color the 0-75 percentile range green for Lp(a)

# Change the following function in your code to color the 0-75 percentile range green for Lp(a)

# Add this function to your code to create a non-linear mapping for Lp(a) percentiles
def map_percentile_to_position(percentile):
    """
    Creates a non-linear mapping of percentiles to visual positions
    to better space out the high percentiles on the Lp(a) chart
    """
    if percentile <= 75:
        # Linear mapping for 0-75th percentile (takes up 40% of visual space)
        return percentile * (40/75)
    elif percentile <= 95:
        # Medium expansion for 75-95th percentile (takes up 30% of visual space)
        return 40 + (percentile - 75) * (30/20)
    else:
        # Highest expansion for 95-100th percentile (takes up 30% of visual space)
        return 70 + (percentile - 95) * (30/5)

# Modified Lp(a) chart function with custom spacing
def create_lpa_chart(title, percentiles, values, patient_value, key_percentiles=None):
    """
    Creates an Lp(a) chart with custom non-linear spacing to better visualize the high percentiles
    """
    # Set default key percentiles if not provided
    if key_percentiles is None:
        key_percentiles = [0, 75, 80, 90, 95, 98, 99, 100]
    
    # Get key values for the specified percentiles
    key_values = []
    for perc in key_percentiles:
        if perc == 0:
            key_values.append(0)  # Minimum value
        elif perc == 100:
            key_values.append(values[-1] * 1.1)  # Maximum value with some margin
        else:
            # Find the nearest percentile or interpolate
            if perc in percentiles:
                idx = percentiles.index(perc)
                key_values.append(values[idx])
            else:
                key_values.append(np.interp(perc, percentiles, values))
    
    # Calculate patient percentile - Lp(a) is handled differently
    patient_percentile = get_percentile(patient_value, lpa_values, lpa_percentiles)
    
    # Determine risk level text for Lp(a) specifically
    if patient_percentile < 75:
        risk_text = "Low Risk"
    elif patient_percentile < 90:
        risk_text = "Moderate Risk"
    else:
        risk_text = "High Risk"
    
    # Create figure
    fig = go.Figure()
    
    # Add a range slider background (full length)
    fig.add_trace(go.Scatter(
        x=[0, 100],
        y=[0, 0],
        mode='lines',
        line=dict(
            color='lightgrey',
            width=10,
        ),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Apply our custom percentile mapping to all key percentiles
    display_positions = [map_percentile_to_position(p) for p in key_percentiles]
    
    # Add the 0-75 percentile segment in green
    fig.add_trace(go.Scatter(
        x=[display_positions[0], display_positions[1]],  # 0 to 75th
        y=[0, 0],
        mode='lines',
        line=dict(
            color='rgba(50, 200, 50, 1)',  # Green color
            width=20,
        ),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Custom colorscale for lpa (for percentiles 75+)
    colorscale = [
        [0.10, 'rgba(50, 200, 50, 1)'],    # Green (at 75th percentile)
        [0.25, 'rgba(220, 220, 50, 1)'],   # Yellow (at 80th percentile)
        [0.50, 'rgba(230, 180, 50, 1)'],   # Light orange (at 90th percentile)
        [0.85, 'rgba(230, 130, 50, 1)'],   # Orange (at 95th percentile)
        [0.98, 'rgba(230, 90, 50, 1)'],    # Dark orange (at 98th percentile)
        [1.0, 'rgba(220, 50, 50, 1)']      # Red (at 100th percentile)
    ]
    
    # Add colored segments based on percentiles for 75th and above
    for i in range(1, len(key_percentiles) - 1):
        # Skip the first segment (0-75) as it's already added
        
        # Get the actual percentile values
        start_percentile = key_percentiles[i]
        end_percentile = key_percentiles[i+1]
        
        # Get the mapped display positions
        start_position = display_positions[i]
        end_position = display_positions[i+1]
        
        # Normalize percentile position for color selection
        color_pos = start_percentile / 100
        
        # Find color from scale
        color = interpolate_color(colorscale, color_pos)
        
        # Add segment
        fig.add_trace(go.Scatter(
            x=[start_position, end_position],
            y=[0, 0],
            mode='lines',
            line=dict(
                color=color,
                width=20,
            ),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Add marker lines and labels for key percentiles
    # Use all key percentiles except for 0 and 100
    display_percentiles = key_percentiles[1:-1]
    display_values = key_values[1:-1]
    display_positions_middle = display_positions[1:-1]
    
    for i, (perc, val, pos) in enumerate(zip(display_percentiles, display_values, display_positions_middle)):
        # Get correct ordinal suffix - ensure we're using integers
        perc_int = int(round(perc))
        suffix = get_ordinal_suffix(perc_int)
        
        # Add percentile label below
        fig.add_annotation(
            x=pos,  # Use mapped position instead of raw percentile
            y=-0.8,
            text=f"{perc_int}<sup>{suffix}</sup>",
            showarrow=False,
            font=dict(size=18, color="#333333", family="Cormorant Garamond"),
        )
        
        # Add value label above with transparent background
        fig.add_annotation(
            x=pos,  # Use mapped position instead of raw percentile
            y=0.7,
            text=f"{int(round(val))}",
            showarrow=False,
            font=dict(size=16, color="#000000", family="Avenir"),
            bgcolor="rgba(255,255,255,0.0)",
            borderpad=4,
        )
    
    # Map the patient percentile to display position
    patient_position = map_percentile_to_position(patient_percentile)
    
    # Add a vertical line for the patient marker
    fig.add_shape(
        type="line",
        x0=patient_position,
        x1=patient_position,
        y0=-0.4,
        y1=0.4,
        line=dict(
            color="#000000",
            width=4,
            dash="solid"
        )
    )
    
    # Add a highlight effect at the top and bottom of the line
    fig.add_trace(go.Scatter(
        x=[patient_position],
        y=[0.4],
        mode="markers",
        marker=dict(
            size=12,
            symbol="triangle-down",
            color="#000000",
            line=dict(width=2, color="white")
        ),
        showlegend=False,
        hoverinfo="none"
    ))
    
    fig.add_trace(go.Scatter(
        x=[patient_position],
        y=[-0.4],
        mode="markers",
        marker=dict(
            size=12,
            symbol="triangle-up",
            color="#000000",
            line=dict(width=2, color="white")
        ),
        name="Patient",
        hovertemplate=f"Patient: {patient_value} mg/dL<br>Percentile: {int(round(patient_percentile))}{get_ordinal_suffix(int(round(patient_percentile)))}"
    ))
    
    # Check if patient percentile is not at a key percentile (with some tolerance)
    tolerance = 4.0  # Allow 4 percentile points of tolerance
    is_at_key_percentile = any(abs(patient_percentile - p) < tolerance for p in display_percentiles)
    
    # Only add annotations if NOT at a key percentile
    if not is_at_key_percentile:
        # Add patient value annotation (above the line)
        fig.add_annotation(
            x=patient_position,  # Use mapped position
            y=0.7,
            text=f"{patient_value}",
            showarrow=False,  # No arrow
            font=dict(size=16, color="#000000", family="Avenir"),
            bgcolor="rgba(255,255,255,0.0)",  # Transparent background
            borderpad=4,
        )
        
        # Get correct ordinal suffix for patient percentile - ensure we're using an integer
        patient_percentile_int = int(round(patient_percentile))
        suffix = get_ordinal_suffix(patient_percentile_int)
        
        # Add percentile annotation (below the line)
        fig.add_annotation(
            x=patient_position,  # Use mapped position
            y=-0.8,
            text=f"{patient_percentile_int}<sup>{suffix}</sup>",
            showarrow=False,  # No arrow
            font=dict(size=18, color="#000000", family="cormorant garamond"),
            bgcolor="rgba(255,255,255,0.0)",  # Transparent background
            borderpad=4,
        )
    
    # Update layout for a cleaner look
    fig.update_layout(
        height=180,
        margin=dict(l=40, r=40, t=20, b=60),
        xaxis=dict(
            range=[-5, 105],  # Consistent range for all charts
            showticklabels=False,
            showgrid=False,
            zeroline=False,
        ),
        yaxis=dict(
            range=[-0.8, 0.8],
            showticklabels=False,
            showgrid=False,
            zeroline=False,
            fixedrange=True
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        showlegend=False,
        hovermode="closest"
    )
    
    return fig

# Helper function to interpolate colors
def interpolate_color(colorscale, val):
    """Interpolate a color from a colorscale based on value"""
    if val <= colorscale[0][0]:
        return colorscale[0][1]
    if val >= colorscale[-1][0]:
        return colorscale[-1][1]
    
    for i in range(len(colorscale)-1):
        if val >= colorscale[i][0] and val <= colorscale[i+1][0]:
            # Linear interpolation between colors
            t = (val - colorscale[i][0]) / (colorscale[i+1][0] - colorscale[i][0])
            
            # Parse color strings to extract RGB values
            color1 = colorscale[i][1]
            color2 = colorscale[i+1][1]
            
            # Check if it's rgba or rgb format
            if color1.startswith('rgba'):
                # For rgba strings like 'rgba(50, 200, 50, 1)'
                values1 = [float(x) for x in color1.strip('rgba()').split(',')]
                values2 = [float(x) for x in color2.strip('rgba()').split(',')]
                
                r = int(values1[0] + t * (values2[0] - values1[0]))
                g = int(values1[1] + t * (values2[1] - values1[1]))
                b = int(values1[2] + t * (values2[2] - values1[2]))
                a = values1[3] + t * (values2[3] - values1[3])
                
                return f'rgba({r}, {g}, {b}, {a})'
            else:
                # For rgb strings 
                values1 = [float(x) for x in color1.strip('rgb()').split(',')]
                values2 = [float(x) for x in color2.strip('rgb()').split(',')]
                
                r = int(values1[0] + t * (values2[0] - values1[0]))
                g = int(values1[1] + t * (values2[1] - values1[1]))
                b = int(values1[2] + t * (values2[2] - values1[2]))
                
                return f'rgb({r}, {g}, {b})'
    
    # Fallback
    return colorscale[-1][1]

# Create the standard lipid charts
apoB_fig = create_standard_chart("ApoB", percentiles, apoB_values, apoB)
nonHDL_fig = create_standard_chart("Non-HDL-C", percentiles, nonHDL_values, nonHDL)
LDL_fig = create_standard_chart("LDL-C", percentiles, LDL_values, LDL)

# Create the Lp(a) chart with its different percentile distribution
lpa_fig = create_lpa_chart("Lp(a)", lpa_percentiles, lpa_values, lpa)

# Display the charts with customized titles but no card containers
st.markdown('<p class="chart-title">ApoB <span style="font-size:0.5em">(mg/dL)</span></p>', unsafe_allow_html=True)
st.plotly_chart(apoB_fig, use_container_width=True, config={'displayModeBar': False})

st.markdown('<p class="chart-title">Non-HDL-C <span style="font-size:0.5em">(mg/dL)</span></p>', unsafe_allow_html=True)
st.plotly_chart(nonHDL_fig, use_container_width=True, config={'displayModeBar': False})

st.markdown('<p class="chart-title">LDL-C <span style="font-size:0.5em">(mg/dL)</span></p>', unsafe_allow_html=True)
st.plotly_chart(LDL_fig, use_container_width=True, config={'displayModeBar': False})

st.markdown('<p class="chart-title">Lp(a) <span style="font-size:0.5em">(mg/dL)</span></p>', unsafe_allow_html=True)
st.plotly_chart(lpa_fig, use_container_width=True, config={'displayModeBar': False})

# Add information section with tabs
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["About Lipid Percentiles", "Risk Interpretation", "Percentile Reference Tables"])

with tab1:
    st.write("""
    ### Understanding Lipid Percentiles
    
    This visualization shows where a patient's lipid values fall within the general population distribution (based on NHANES data for people not on lipid-lowering medications).
    
    - **ApoB (Apolipoprotein B)**: A protein found in lipoproteins such as LDL, VLDL, and Lp(a). It's considered a more accurate predictor of cardiovascular risk than LDL-C alone.
    
    - **Non-HDL-C**: Represents all atherogenic cholesterol particles. Calculated as Total Cholesterol minus HDL-C.
    
    - **LDL-C**: Low-density lipoprotein cholesterol, often referred to as "bad cholesterol".
    
    - **Lp(a)**: Lipoprotein(a) is a genetically determined variant of LDL and is considered an independent risk factor for cardiovascular disease.
    """)

with tab2:
    st.write("""
    ### Interpreting Risk Levels
    
    **Low Risk** (≤ 20th percentile):
    - Values in this range are generally associated with lower cardiovascular risk.
    - For most adults without other risk factors, maintaining levels in this range is desirable.
    
    **Moderate Risk** (21st - 50th percentile):
    - Values in this range represent average levels in the population.
    - May warrant attention in individuals with other risk factors.
    
    **High Risk** (> 50th percentile):
    - Values in this range are higher than average and may indicate increased cardiovascular risk.
    - May warrant consideration of lipid-lowering therapies depending on overall risk assessment.
    
    ### Lp(a) Interpretation
    
    The distribution of Lp(a) in the population is highly skewed, with most people having low levels:
    
    - 75th percentile: >47 mg/dL
    - 80th percentile: >60 mg/dL
    - 90th percentile: >90 mg/dL
    - 95th percentile: >116 mg/dL
    - 99th percentile: >180 mg/dL
    
    Values >50 mg/dL may indicate increased cardiovascular risk independent of other lipid markers.
    """)

with tab3:
    st.subheader("Complete Percentile Reference Tables")
    
    # Ensure correct ordinal suffixes in tables
    percentile_labels = [f"{p}{get_ordinal_suffix(p)}" for p in percentiles]
    lpa_percentile_labels = [f"{p}{get_ordinal_suffix(p)}" for p in lpa_percentiles]
    
    # Create dataframes for each lipid marker with all percentiles
    apob_df = pd.DataFrame({
        'Percentile': percentile_labels,
        'ApoB (mg/dL)': apoB_values
    })
    
    nonhdl_df = pd.DataFrame({
        'Percentile': percentile_labels,
        'Non-HDL-C (mg/dL)': nonHDL_values
    })
    
    ldl_df = pd.DataFrame({
        'Percentile': percentile_labels,
        'LDL-C (mg/dL)': LDL_values
    })
    
    lpa_df = pd.DataFrame({
        'Percentile': lpa_percentile_labels,
        'Lp(a) (mg/dL)': lpa_values
    })
    
    # Display the tables with formatting
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ApoB Percentiles")
        st.dataframe(apob_df.style.format({'ApoB (mg/dL)': '{:.0f}'}))
        
        st.markdown("#### Non-HDL-C Percentiles")
        st.dataframe(nonhdl_df.style.format({'Non-HDL-C (mg/dL)': '{:.0f}'}))
    
    with col2:
        st.markdown("#### LDL-C Percentiles")
        st.dataframe(ldl_df.style.format({'LDL-C (mg/dL)': '{:.0f}'}))
        
        st.markdown("#### Lp(a) Percentiles")
        st.dataframe(lpa_df.style.format({'Lp(a) (mg/dL)': '{:.0f}'}))
    
    st.info("""
    These values represent population percentiles from NHANES data for individuals not taking lipid-lowering medications.
    Interpolated values may be used to estimate percentiles between the reference points shown in the tables above.
    """)

# Replace the current export section with this simplified version
# that works on Streamlit Cloud

import io
import base64
from PIL import Image
import plotly.graph_objects as go

# Add a section for exporting charts
st.markdown("---")
st.header("Export Charts")
st.write("Use these buttons to download the charts as interactive HTML files.")

# Function to create an HTML download link for a Plotly figure
def get_plotly_html_download_link(fig, filename, text, title=None):
    """
    Generates a link to download a Plotly figure as an HTML file
    """
    # Add title if provided
    if title:
        fig.update_layout(
            title={
                'text': title,
                'font': {'size': 24, 'family': 'Cormorant Garamond', 'color': '#2c3e50'},
                'x': 0.5,
                'xanchor': 'center',
                'y': 0.95
            }
        )
    
    # Convert the figure to HTML
    buffer = io.StringIO()
    fig.write_html(buffer)
    html_bytes = buffer.getvalue().encode()
    
    # Encode as base64
    b64 = base64.b64encode(html_bytes).decode()
    
    # Create the download link
    href = f'<a href="data:text/html;base64,{b64}" download="{filename}.html">{text}</a>'
    return href

# Create a row of download buttons for charts with patient markers
col1, col2, col3, col4 = st.columns(4)

with col1:
    # Re-create ApoB figure
    apoB_fig_export = create_standard_chart("ApoB", percentiles, apoB_values, apoB)
    apoB_link = get_plotly_html_download_link(apoB_fig_export, "ApoB_Chart", "Download ApoB Chart", "ApoB (mg/dL)")
    st.markdown(apoB_link, unsafe_allow_html=True)

with col2:
    nonHDL_fig_export = create_standard_chart("Non-HDL-C", percentiles, nonHDL_values, nonHDL)
    nonHDL_link = get_plotly_html_download_link(nonHDL_fig_export, "NonHDL_Chart", "Download Non-HDL Chart", "Non-HDL-C (mg/dL)")
    st.markdown(nonHDL_link, unsafe_allow_html=True)

with col3:
    LDL_fig_export = create_standard_chart("LDL-C", percentiles, LDL_values, LDL)
    LDL_link = get_plotly_html_download_link(LDL_fig_export, "LDL_Chart", "Download LDL Chart", "LDL-C (mg/dL)")
    st.markdown(LDL_link, unsafe_allow_html=True)

with col4:
    # Use the custom spacing for Lp(a)
    lpa_fig_export = create_lpa_chart("Lp(a)", lpa_percentiles, lpa_values, lpa)
    lpa_link = get_plotly_html_download_link(lpa_fig_export, "Lpa_Chart", "Download Lp(a) Chart", "Lp(a) (mg/dL)")
    st.markdown(lpa_link, unsafe_allow_html=True)

# Create a row of download buttons for spectrum bars only
st.write("Or download the spectrum bars only (without patient markers):")

col1, col2, col3, col4 = st.columns(4)

# Function to create a chart without patient markers
def create_bar_only_chart(title, percentiles, values, key_percentiles=None):
    """
    Creates a chart with just the colored spectrum bars, no patient markers
    """
    if title == "Lp(a)":
        # Create Lp(a) chart without patient marker
        fig = create_lpa_chart(title, lpa_percentiles, lpa_values, 0)
    else:
        # Create standard chart without patient marker
        fig = create_standard_chart(title, percentiles, values, values[0])
    
    # Safely filter out traces related to patient markers
    new_data = []
    for trace in fig.data:
        # Only include traces that don't have 'Patient' in their name
        # Use hasattr to safely check if the trace has a name attribute
        if not hasattr(trace, 'name') or trace.name is None or 'Patient' not in trace.name:
            new_data.append(trace)
    
    fig.data = new_data
    
    # Remove all shapes (patient line)
    fig.layout.shapes = []
    
    return fig

with col1:
    apoB_bar_fig = create_bar_only_chart("ApoB", percentiles, apoB_values)
    apoB_bar_link = get_plotly_html_download_link(apoB_bar_fig, "ApoB_Bar_Only", "Download ApoB Bar Only", "ApoB (mg/dL)")
    st.markdown(apoB_bar_link, unsafe_allow_html=True)

with col2:
    nonHDL_bar_fig = create_bar_only_chart("Non-HDL-C", percentiles, nonHDL_values)
    nonHDL_bar_link = get_plotly_html_download_link(nonHDL_bar_fig, "NonHDL_Bar_Only", "Download Non-HDL Bar Only", "Non-HDL-C (mg/dL)")
    st.markdown(nonHDL_bar_link, unsafe_allow_html=True)

with col3:
    LDL_bar_fig = create_bar_only_chart("LDL-C", percentiles, LDL_values)
    LDL_bar_link = get_plotly_html_download_link(LDL_bar_fig, "LDL_Bar_Only", "Download LDL Bar Only", "LDL-C (mg/dL)")
    st.markdown(LDL_bar_link, unsafe_allow_html=True)

with col4:
    lpa_bar_fig = create_bar_only_chart("Lp(a)", lpa_percentiles, lpa_values)
    lpa_bar_link = get_plotly_html_download_link(lpa_bar_fig, "Lpa_Bar_Only", "Download Lp(a) Bar Only", "Lp(a) (mg/dL)")
    st.markdown(lpa_bar_link, unsafe_allow_html=True)

# Alternative approach for image download using Streamlit's download button
st.markdown("---")
st.header("Alternative Export Option")
st.write("You can also take a screenshot of the charts directly from your browser for maximum quality.")
st.write("1. Press the 'View fullscreen' button at the top-right of each chart")
st.write("2. Use your browser's screenshot tool or press Print Screen")
st.write("3. Paste the screenshot into your document or presentation software")

# Disclaimer
st.markdown("""
<div style="background-color: #f8f9fa; padding: 10px; border-radius: 5px; margin-top: 20px;">
    <p style="font-size: 12px; color: #6c757d; margin: 0;">
        <strong>Disclaimer:</strong> This tool is for educational purposes only and should not be used for medical decision-making without consulting a healthcare professional.
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar additional information
st.sidebar.markdown("---")
st.sidebar.info("""
This visualization tool helps compare individual lipid profiles to population reference ranges based on NHANES data.

**How to use:**
1. Enter the patient's lipid values in the fields above
2. View where these values fall on the population percentile charts
3. Refer to the tabs below for interpretation guidance
""")