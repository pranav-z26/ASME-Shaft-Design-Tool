# ASME Code-Compliant Shaft Design Suite

An interactive Streamlit web application for sizing solid and hollow transmission shafts according to ASME recommendations (ASME B106.1M).

---

## 🛠 Locally Deploy the Application

### Prerequisites
- Python 3.9 or newer
- Git (optional, for version control)

### Project layout
Ensure the project files are together in a single folder:

```text
shaft_design_app/
├── app.py
├── shaft_designer.py
├── report_generator.py
├── requirements.txt
└── README.md
```

### Setup (virtual environment and dependencies)
Run these commands from the project folder.

On macOS / Linux:

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

On Windows (PowerShell):

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Run the Streamlit app

```bash
streamlit run app.py
```

The app should open in your browser at http://localhost:8501.

---

## Verification Example
You can validate the application's calculations with this reference scenario.

Input values:
- Power: 15 kW
- Speed: 960 RPM
- Bending moment M: 500,000 N·mm
- Bending shock factor Kb: 1.5
- Torsional shock factor Kt: 1.0
- Safety factor (FOS): 1.0
- Keyway: Yes (25% strength reduction)
- Material: EN8 (Yield strength S_yt = 280 MPa, Ultimate strength S_ut = 550 MPa)

Summary of the calculation steps (values rounded for clarity):

1. Applied torque T:

   T = 9550 * P / N = 9550 * 15 / 960 ≈ 149.22 N·m = 149,218.75 N·mm

2. Allowable shear stress τ_allow (ASME rule):

   τ_base = min(0.3 × S_yt, 0.18 × S_ut) = min(0.3 × 280, 0.18 × 550) = 84.0 MPa

   Apply keyway reduction: τ_allow = 84.0 × 0.75 = 63.0 MPa

3. Equivalent twisting moment T_e:

   T_e = sqrt((Kb·M)^2 + (Kt·T)^2)

   Using the inputs: T_e ≈ 764,700.1 N·mm

4. Minimum solid shaft diameter d:

   d = (16·T_e / (π·τ_allow))^(1/3) ≈ 39.54 mm

5. Round up to standard size: recommended diameter = 40 mm

---

## How to verify outputs in the app
1. Start the app with `streamlit run app.py`.
2. Enter the verification inputs above in the sidebar.
3. Confirm the calculated minimum diameter shows approximately **39.54 mm** and the recommended standard diameter is **40 mm**.
4. Optionally, generate the PDF report and verify the numbers match.

If you find issues or want additional examples added to this README, open an issue or send a patch.
