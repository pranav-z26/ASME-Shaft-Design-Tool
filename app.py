"""
app.py
Interactive user interface built with Streamlit for real-time mechanical shaft design calculations.
"""

import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import os
from shaft_designer import ShaftDesign, MATERIAL_DATABASE
from report_generator import generate_pdf_report

# Page Configuration
st.set_page_config(
    page_title="ASME Shaft Design Tool",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application Header
st.title("⚙️ Professional Shaft Design & Optimization Tool")
st.markdown("""
Analytical utility for solid and hollow shafts subjected to combined bending and torsional loads.
Calculations align with standard **ASME B106.1M** recommendations.
""")

# Sidebar Input panel
st.sidebar.header("🔧 Primary Design Inputs")

power = st.sidebar.number_input("Power (kW)", min_value=0.1, value=15.0, step=1.0, help="Transmitted power")
speed = st.sidebar.number_input("Speed (RPM)", min_value=1.0, value=960.0, step=10.0, help="Rotational operational speed")
bending = st.sidebar.number_input("Bending Moment (N-mm)", min_value=0.0, value=500000.0, step=10000.0, help="Applied peak bending moment")

st.sidebar.markdown("---")
st.sidebar.subheader("ASME Factors & Safety Margin")
kb = st.sidebar.slider("Bending Fatigue Factor (Kb)", 1.0, 3.0, 1.5, 0.1, help="Combines shock and fatigue limits")
kt = st.sidebar.slider("Torsional Fatigue Factor (Kt)", 1.0, 3.0, 1.0, 0.1, help="Combines shock and fatigue limits")
fos = st.sidebar.number_input("Design Factor of Safety (FOS)", min_value=1.0, max_value=10.0, value=1.0, step=0.1)

st.sidebar.markdown("---")
st.sidebar.subheader("Material Profile")
mat_selected = st.sidebar.selectbox("Select Shaft Material", list(MATERIAL_DATABASE.keys()))

st.sidebar.markdown("---")
st.sidebar.subheader("Geometric Modifications")
has_keyway = st.sidebar.checkbox("Include Keyways (Reduces allowable stress by 25%)", value=True)

# Advanced Panel
st.sidebar.markdown("### 🛠️ Advanced Options")
is_hollow = st.sidebar.checkbox("Design as Hollow Shaft", value=False)
k_ratio = 0.0
if is_hollow:
    k_ratio = st.sidebar.slider("Inner to Outer Diameter Ratio (k = di/do)", 0.1, 0.8, 0.5, 0.05)

shaft_length = st.sidebar.number_input("Effective Shaft Length (mm)", min_value=50.0, value=500.0, step=10.0)

# Main Screen Output Logic
try:
    # Run calculations using back-end class
    design = ShaftDesign(
        power_kw=power,
        speed_rpm=speed,
        bending_moment=bending,
        kb=kb,
        kt=kt,
        fos=fos,
        material=mat_selected,
        has_keyway=has_keyway,
        is_hollow=is_hollow,
        inner_outer_ratio=k_ratio,
        shaft_length_mm=shaft_length
    )

    # 3-Column Quick Metrics Layout
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Calculated Torque", value=f"{design.torque_nmm:,.1f} N-mm")
    with col2:
        st.metric(label="Equivalent Torque (Te)", value=f"{design.equivalent_torque:,.1f} N-mm")
    with col3:
        st.metric(label="Minimum Calc. Diameter", value=f"{design.calculated_diameter:.2f} mm")
    with col4:
        st.metric(label="Recommended Size (do)", value=f"{design.recommended_diameter} mm")

    st.markdown("---")

    # Layout for charts and engineering report
    main_col1, main_col2 = st.columns([3, 2])

    with main_col1:
        st.subheader("📊 Performance & Visualizations")
        
        # Tabs for different plots
        tab1, tab2, tab3 = st.tabs(["Shaft Loading Profile", "Diameter Comparison", "Deflection Estimator"])
        
        with tab1:
            # Simple Matplotlib Loading Visualizer
            fig, ax = plt.subplots(figsize=(6, 2.5))
            L = design.shaft_length_mm
            ax.plot([0, L], [0, 0], color='grey', lw=6, label="Shaft Axis")
            # Bearings
            ax.plot([0], [0], '^', color='black', ms=12, label="Left Bearing")
            ax.plot([L], [0], '^', color='black', ms=12, label="Right Bearing")
            # Concentrated Center Load
            ax.annotate('', xy=(L/2, -0.1), xytext=(L/2, 1.0),
                        arrowprops=dict(facecolor='red', shrink=0.05, width=2, headwidth=8))
            ax.text(L/2, 1.1, f"F_eq: {design.central_force_n:.1f} N\n(M: {design.bending_moment:.0f} N-mm)", 
                    color='red', ha='center', fontsize=9)
            
            # Labels
            ax.set_xlim(-L*0.1, L*1.1)
            ax.set_ylim(-1.5, 2.0)
            ax.axis('off')
            ax.set_title("Simplified Symmetrical Loading Concept", fontsize=10, fontweight='bold', pad=10)
            st.pyplot(fig)
            plt.close()

        with tab2:
            # Comparison bar plot
            fig, ax = plt.subplots(figsize=(6, 3))
            categories = ["Calc. Min", "Standard Recommended"]
            values = [design.calculated_diameter, design.recommended_diameter]
            
            if design.is_hollow:
                categories.extend(["Calc. Inner", "Recommended Inner"])
                values.extend([design.calculated_inner_diameter, design.recommended_inner_diameter])
                
            bars = ax.bar(categories, values, color=['#A0AEC0', '#2B6CB0', '#CBD5E0', '#4299E1'], width=0.4)
            ax.set_ylabel("Diameter (mm)", fontsize=9)
            ax.set_title("Shaft Geometric Profiles Comparison", fontsize=10, fontweight='bold')
            ax.tick_params(axis='both', labelsize=8)
            for bar in bars:
                yval = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2, yval + 1, f"{yval:.1f} mm", ha='center', va='bottom', fontsize=8)
            st.pyplot(fig)
            plt.close()

        with tab3:
            # Simple Static Elastic Deflection curve representation
            fig, ax = plt.subplots(figsize=(6, 3))
            x_vals = np.linspace(0, design.shaft_length_mm, 100)
            # Elastic curve equation for simple support, point load at center:
            # y = F*x / (48*E*I) * (3*L^2 - 4*x^2) for x <= L/2
            E_mpa = design.mat_props["E"] * 1000.0
            I = design.I_mm4
            F = design.central_force_n
            L_val = design.shaft_length_mm
            
            y_vals = []
            for x in x_vals:
                if x <= L_val / 2:
                    y = (F * x / (48.0 * E_mpa * I)) * (3.0 * L_val**2 - 4.0 * x**2)
                else:
                    x_sym = L_val - x
                    y = (F * x_sym / (48.0 * E_mpa * I)) * (3.0 * L_val**2 - 4.0 * x_sym**2)
                y_vals.append(-y) # Negative represents downward deformation
                
            ax.plot(x_vals, y_vals, 'b--', label='Deformed Profile')
            ax.axhline(0, color='black', lw=0.5)
            ax.set_xlabel("Shaft Length Span (mm)", fontsize=8)
            ax.set_ylabel("Deflection (mm)", fontsize=8)
            ax.set_title("Elastic Deflection Estimative Curve (Point Load)", fontsize=10, fontweight='bold')
            ax.tick_params(axis='both', labelsize=8)
            ax.grid(True, linestyle=':', alpha=0.6)
            st.pyplot(fig)
            plt.close()

    with main_col2:
        st.subheader("📋 Static Analytical Review")
        
        # Design Status Banner
        if design.recommended_diameter >= design.calculated_diameter:
            st.success("✅ DESIGN CRITERIA CONFORMS TO STRESS BOUNDARIES")
        else:
            st.error("❌ CRITERIA FAIL: Geometric design violates maximum allowable limits")

        # Key metrics table representation
        metrics_table = f"""
        | Evaluation Characteristic | Analytical Value | Design Target |
        | :--- | :--- | :--- |
        | **Material Selected** | {design.material_name} | -- |
        | **Yield Strength (Syt)** | {design.mat_props['S_yt']:.1f} MPa | -- |
        | **ASME Allowable Shear (τ)** | {design.allowable_stress:.2f} MPa | Base Limit |
        | **Max Induced Shear (τ_ind)** | {design.induced_shear_stress:.2f} MPa | < Allowable |
        | **Calculated Outer Dia.** | {design.calculated_diameter:.2f} mm | Min Profile |
        | **Standard Nom. Dia. (do)** | {design.recommended_diameter} mm | Match ISO Standard |
        | **Estimated Deflection (δ)** | {design.total_deflection_mm:.4f} mm | Deflection Limit |
        | **Critical Dynamic Speed** | {design.critical_speed_rpm:,.1f} RPM | Operational Limit |
        """
        st.markdown(metrics_table)

        st.markdown("### 📄 Technical Documentation & PDF Export")
        st.write("Generate a formatted compliance report of the calculations for review or presentation.")
        
        if st.button("Compile PDF Report"):
            report_filename = "shaft_compliance_report.pdf"
            generate_pdf_report(design, filepath=report_filename)
            
            with open(report_filename, "rb") as file:
                btn = st.download_button(
                    label="Download PDF Report Document",
                    data=file,
                    file_name=report_filename,
                    mime="application/pdf"
                )

except Exception as e:
    st.error(f"Critical execution error during mathematical calculation: {str(e)}")
    st.info("Check input configurations for negative, null, or inconsistent values.")