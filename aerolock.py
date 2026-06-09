import streamlit as st
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

st.set_page_config(page_title="AEROLOCK — F1 Porpoising Simulator", layout="wide", page_icon="🏎️")

st.title("🏎️ AEROLOCK — F1 Porpoising Physics Simulator")
st.markdown("### Real-time ground effect aerodynamic stall and porpoising simulator")
st.divider()
st.sidebar.header("⚙️ Car Parameters")
speed = st.sidebar.slider("Car Speed (km/h)", 100, 350, 250, 5)
ride_height = st.sidebar.slider("Ride Height (mm)", 2, 30, 10, 1)
downforce_coeff = st.sidebar.slider("Downforce Coefficient", 0.5, 3.0, 1.8, 0.1)
stiffness = st.sidebar.slider("Suspension Stiffness (N/mm)", 50, 300, 150, 10)

st.sidebar.divider()
st.info("📋 Based on 2022-2023 FIA Technical Regulations — Ground Effect Era. Mercedes W14 porpoising data referenced from 2022 Bahrain GP and 2023 season telemetry reports.")
st.sidebar.header("🏁 Select Team")
team = st.sidebar.selectbox("Team", ["Mercedes W14 (2023)", "Red Bull RB19", "Ferrari SF-23", "Custom"])

if team == "Mercedes W14 (2023)":
    ride_height = 7
    downforce_coeff = 2.1
    stiffness = 200
elif team == "Red Bull RB19":
    ride_height = 12
    downforce_coeff = 1.9
    stiffness = 180
elif team == "Ferrari SF-23":
    ride_height = 10
    downforce_coeff = 2.0
    stiffness = 160

# Physics calculations
speed_ms = speed / 3.6
dynamic_pressure = 0.5 * 1.225 * speed_ms**2
downforce = downforce_coeff * dynamic_pressure * 1.5
car_weight = 798 * 9.81

# Porpoising threshold
critical_ride_height = 8
porpoising_severity = max(0, (critical_ride_height - ride_height) / critical_ride_height)
porpoising_frequency = 2 + (speed / 100) * 3
porpoising_amplitude = porpoising_severity * 15 * (downforce_coeff / 2)

# Status
if porpoising_severity > 0.6:
    st.error(f"🚨 SEVERE PORPOISING DETECTED — Amplitude: {porpoising_amplitude:.1f}mm")
elif porpoising_severity > 0.3:
    st.warning(f"⚠️ MODERATE PORPOISING — Amplitude: {porpoising_amplitude:.1f}mm")
else:
    st.success(f"✅ STABLE — No significant porpoising detected")

# Metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Speed", f"{speed} km/h")
col2.metric("Downforce", f"{downforce/1000:.1f} kN")
col3.metric("Bounce Frequency", f"{porpoising_frequency:.1f} Hz")
col4.metric("Bounce Amplitude", f"{porpoising_amplitude:.1f} mm")

st.divider()

col_left, col_right = st.columns(2)

with col_left:
    st.subheader("🌊 Porpoising Motion Simulation")
    t = np.linspace(0, 2, 1000)
    
    if porpoising_severity > 0:
        bounce = porpoising_amplitude * np.sin(2 * np.pi * porpoising_frequency * t) * np.exp(-0.1 * t * (1 - porpoising_severity))
        envelope_upper = porpoising_amplitude * np.exp(-0.1 * t * (1 - porpoising_severity))
        envelope_lower = -porpoising_amplitude * np.exp(-0.1 * t * (1 - porpoising_severity))
    else:
        bounce = np.zeros_like(t)
        envelope_upper = np.zeros_like(t)
        envelope_lower = np.zeros_like(t)

    fig1 = go.Figure()
    fig1.add_trace(go.Scatter(
        x=t, y=bounce,
        mode='lines',
        name='Car Displacement',
        line=dict(color='cyan', width=2)
    ))
    fig1.add_trace(go.Scatter(
        x=t, y=envelope_upper,
        mode='lines',
        name='Envelope',
        line=dict(color='red', width=1, dash='dash')
    ))
    fig1.add_trace(go.Scatter(
        x=t, y=envelope_lower,
        mode='lines',
        showlegend=False,
        line=dict(color='red', width=1, dash='dash')
    ))
    fig1.add_hline(y=0, line_color='white', line_width=1)
    fig1.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#0a0a0a',
        xaxis_title='Time (seconds)',
        yaxis_title='Vertical Displacement (mm)',
        height=350
    )
    st.plotly_chart(fig1, use_container_width=True)

with col_right:
    st.subheader("📊 Downforce vs Ride Height")
    ride_heights = np.linspace(2, 30, 100)
    downforces = []
    for rh in ride_heights:
        df = downforce_coeff * dynamic_pressure * 1.5
        ground_effect_boost = max(0, (15 - rh) / 15) * 0.5
        stall = max(0, (5 - rh) / 5) * 0.8
        df = df * (1 + ground_effect_boost - stall)
        downforces.append(df / 1000)

    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=ride_heights,
        y=downforces,
        mode='lines',
        line=dict(color='orange', width=3),
        fill='tozeroy',
        fillcolor='rgba(255,140,0,0.1)'
    ))
    fig2.add_vline(
        x=ride_height,
        line_color='cyan',
        line_dash='dash',
        annotation_text=f"Current: {ride_height}mm",
        annotation_font_color='cyan'
    )
    fig2.add_vline(
        x=critical_ride_height,
        line_color='red',
        line_dash='dash',
        annotation_text="Stall threshold",
        annotation_font_color='red'
    )
    fig2.update_layout(
        template='plotly_dark',
        paper_bgcolor='#0a0a0a',
        plot_bgcolor='#0a0a0a',
        xaxis_title='Ride Height (mm)',
        yaxis_title='Downforce (kN)',
        height=350
    )
    st.plotly_chart(fig2, use_container_width=True)

st.subheader("⚡ G-Force on Driver")
g_force = porpoising_amplitude * porpoising_frequency**2 * (2 * np.pi)**2 / (9.81 * 1000)
g_time = np.linspace(0, 2, 1000)
g_signal = g_force * np.abs(np.sin(2 * np.pi * porpoising_frequency * g_time))

fig3 = go.Figure()
fig3.add_trace(go.Scatter(
    x=g_time,
    y=g_signal,
    mode='lines',
    line=dict(color='#ff4444', width=2),
    fill='tozeroy',
    fillcolor='rgba(255,68,68,0.2)'
))
fig3.add_hline(y=2, line_color='yellow', line_dash='dash', annotation_text="Discomfort threshold (2G)", annotation_font_color='yellow')
fig3.add_hline(y=4, line_color='red', line_dash='dash', annotation_text="Dangerous threshold (4G)", annotation_font_color='red')
fig3.update_layout(
    template='plotly_dark',
    paper_bgcolor='#0a0a0a',
    plot_bgcolor='#0a0a0a',
    xaxis_title='Time (seconds)',
    yaxis_title='Vertical G-Force',
    height=300
)
st.plotly_chart(fig3, use_container_width=True)

st.divider()
st.markdown("*Built by Atharv Shukla | AEROLOCK — F1 Porpoising Physics Simulator | Aerospace Engineering Portfolio*")