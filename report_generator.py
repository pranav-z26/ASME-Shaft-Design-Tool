"""
report_generator.py
Handles the compilation of analytical calculations and specifications into a professional PDF report.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(design_obj, filepath="shaft_design_report.pdf"):
    """
    Generates a structured PDF design report.
    """
    doc = SimpleDocTemplate(filepath, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    
    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary_color = colors.HexColor("#1A365D")   # Deep Slate Blue
    secondary_color = colors.HexColor("#2B6CB0") # Medium Blue
    text_color = colors.HexColor("#2D3748")      # Dark Grey
    
    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=primary_color,
        spaceAfter=15
    )
    
    h2_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=secondary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyTextCustom',
        parent=styles['Normal'],
        fontSize=10,
        textColor=text_color,
        leading=14
    )

    # Document Header
    story.append(Paragraph("SHAFT DESIGN COMPLIANCE REPORT", title_style))
    story.append(Paragraph("<b>Standard:</b> ASME Code recommendations for Transmission Shafting", body_style))
    story.append(Paragraph(f"<b>Material Selected:</b> {design_obj.material_name}", body_style))
    story.append(Spacer(1, 10))

    # Table 1: Input Parameters
    story.append(Paragraph("1. Design Input Parameters", h2_style))
    input_data = [
        [Paragraph("<b>Parameter</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Description</b>", body_style)],
        ["Power (P)", f"{design_obj.power_kw} kW", "Transmitted shaft power"],
        ["Rotational Speed (N)", f"{design_obj.speed_rpm} RPM", "Operational speed"],
        ["Bending Moment (M)", f"{design_obj.bending_moment:,.1f} N-mm", "Peak bending load"],
        ["Fatigue Factors (Kb / Kt)", f"{design_obj.kb} / {design_obj.kt}", "ASME combined shock/fatigue modifiers"],
        ["Specified FOS", f"{design_obj.fos}", "Design margin multiplier"],
        ["Keyway Cutout Included", "Yes (25% Stress Reduction Applied)" if design_obj.has_keyway else "No", "Keyway geometry check"]
    ]
    
    t1 = Table(input_data, colWidths=[150, 120, 230])
    t1.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('TEXTCOLOR', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t1)
    story.append(Spacer(1, 15))

    # Table 2: Material Properties
    story.append(Paragraph("2. Mechanical Properties (Database Reference)", h2_style))
    mat_data = [
        [Paragraph("<b>Property</b>", body_style), Paragraph("<b>Value</b>", body_style)],
        ["Yield Strength (S_yt)", f"{design_obj.mat_props['S_yt']} MPa"],
        ["Ultimate Tensile Strength (S_ut)", f"{design_obj.mat_props['S_ut']} MPa"],
        ["Modulus of Elasticity (E)", f"{design_obj.mat_props['E']} GPa"],
        ["Density", f"{design_obj.mat_props['density']} kg/m³"],
        ["Design Allowable Shear Stress (t_allow)", f"{design_obj.allowable_stress:.2f} MPa"]
    ]
    
    t2 = Table(mat_data, colWidths=[250, 250])
    t2.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t2)
    story.append(Spacer(1, 15))

    # Table 3: Calculations & Results
    story.append(Paragraph("3. Design Calculations & Geometric Output", h2_style))
    
    hollow_type = "Hollow" if design_obj.is_hollow else "Solid"
    res_data = [
        [Paragraph("<b>Output Metric</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Equations / Notes</b>", body_style)],
        ["Calculated Torque (T)", f"{design_obj.torque_nmm:,.1f} N-mm", "T = (9550 * P / N) * 1000"],
        ["Equivalent Twisting Moment (Te)", f"{design_obj.equivalent_torque:,.1f} N-mm", "Te = sqrt((Kb*M)² + (Kt*T)²)"],
        ["Shaft Profile Type", hollow_type, "Structural geometry option"],
        ["Analytical Minimum Diameter", f"{design_obj.calculated_diameter:.2f} mm", "Calculated stress boundary limit"],
        ["<b>Recommended Standard Diameter</b>", f"<b>{design_obj.recommended_diameter} mm</b>", "Rounded to nearest ISO standard profile"],
    ]
    
    if design_obj.is_hollow:
        res_data.append(["Calculated Inner Diameter", f"{design_obj.calculated_inner_diameter:.2f} mm", "Based on ratio (k)"])
        res_data.append(["Recommended Inner Diameter", f"{design_obj.recommended_inner_diameter:.2f} mm", f"Based on ratio k = {design_obj.k}"])

    t3 = Table(res_data, colWidths=[180, 120, 200])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#EDF2F7")),
        ('LINEBELOW', (0,-1), (-1,-1), 1.5, primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t3)
    story.append(Spacer(1, 15))

    # Table 4: Advanced Modeling
    story.append(Paragraph("4. Secondary Dynamic & Deflection Analysis", h2_style))
    adv_data = [
        [Paragraph("<b>Analysis</b>", body_style), Paragraph("<b>Value</b>", body_style), Paragraph("<b>Comments</b>", body_style)],
        ["Max Induced Shear Stress (tau)", f"{design_obj.induced_shear_stress:.2f} MPa", "Induced stress under service load"],
        ["Computed Margin / FOS", f"{design_obj.actual_fos:.2f}", "Margin against material shear limit"],
        ["Est. Total Deflection", f"{design_obj.total_deflection_mm:.4f} mm", "Combined load & weight contribution"],
        ["First Critical Speed", f"{design_obj.critical_speed_rpm:,.1f} RPM", "Estimated fundamental resonant frequency"],
        ["Bearing Reaction forces", f"{design_obj.bearing_reaction_n:.1f} N", "Simplified symmetrical support model"]
    ]
    
    t4 = Table(adv_data, colWidths=[180, 120, 200])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#E2E8F0")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E0")),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t4)
    story.append(Spacer(1, 20))

    # Conclusion Paragraph
    story.append(Paragraph("<b>Design Verification Statement:</b>", h2_style))
    if design_obj.recommended_diameter >= design_obj.calculated_diameter:
        statement = (
            f"The recommended outer diameter of <b>{design_obj.recommended_diameter} mm</b> satisfies the "
            f"analytical requirements under the applied torsional and bending conditions with a margin of safety. "
            f"Real-world fatigue, environmental effects, and key stress concentration zones must be independently validated."
        )
    else:
        statement = "The geometry does not meet stress criteria requirements. Review selected material properties and input configurations."
        
    story.append(Paragraph(statement, body_style))
    
    doc.build(story)