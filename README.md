# ASME Code Compliant Shaft Design Suite

An interactive web application built with Streamlit for sizing solid and hollow transmission shafts. Sizing calculations adhere to the guidelines recommended by **ASME B106.1M** standards.

---

## 🛠️ Locally Deploying the Application

### Prerequisites
Make sure you have Python 3.9+ installed on your computer.

### Step 1: Clone or Extract the App Directory
Ensure all scripts are placed in the same folder:
```text
shaft_design_app/
├── app.py
├── shaft_designer.py
├── report_generator.py
└── requirements.txt

Step 2: Set Up a Virtual Environment & Install Dependencies
Open your command terminal inside the directory and run:
code
Bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install the required Python packages
pip install -r requirements.txt
Step 3: Run the Streamlit GUI
Execute the following terminal command to boot the web tool:
code
Bash
streamlit run app.py
A browser window should open automatically at http://localhost:8501.
📐 Verification and Verification Calculation
The application's mathematical calculations can be validated using the following reference scenario:
Test Input Configuration
Power (
P
P
): 15 kW
Speed (
N
N
): 960 RPM
Bending Moment (
M
M
): 500,000 N-mm
Bending Shock Factor (
K
b
K 
b
​
 
): 1.5
Torsional Shock Factor (
K
t
K 
t
​
 
): 1.0
Safety Factor (FOS): 1.0
Keyway Presence: Yes (25% ASME Stress Reduction)
Material: EN8 (Medium Carbon Steel)
S
y
t
S 
yt
​
 
 (Yield Strength) = 280.0 MPa
S
u
t
S 
ut
​
 
 (Ultimate Strength) = 550.0 MPa
Step-by-Step Analytical Calculations
1. Applied Torque (
T
T
)
T
=
9550
×
P
N
=
9550
×
15
960
=
149.21875
 N-m
T= 
N
9550×P
​
 = 
960
9550×15
​
 =149.21875 N-m

T
=
149
,
218.75
 N-mm
T=149,218.75 N-mm
2. Allowable Stress Boundaries (
τ
allow
τ 
allow
​
 
)
Under ASME guidelines:
τ
base
=
min
⁡
(
0.3
×
S
y
t
,
0.18
×
S
u
t
)
τ 
base
​
 =min(0.3×S 
yt
​
 ,0.18×S 
ut
​
 )
0.3
×
280.0
 MPa
=
84.0
 MPa
0.3×280.0 MPa=84.0 MPa
0.18
×
550.0
 MPa
=
99.0
 MPa
0.18×550.0 MPa=99.0 MPa
τ
base
=
84.0
 MPa
τ 
base
​
 =84.0 MPa
Applying Keyway reduction (25% strength discount, equivalent to multiplying by 0.75):
τ
allow
=
84.0
×
0.75
=
63.0
 MPa
τ 
allow
​
 =84.0×0.75=63.0 MPa
3. Equivalent Twisting Moment (
T
e
T 
e
​
 
)
T
e
=
(
K
b
×
M
)
2
+
(
K
t
×
T
)
2
T 
e
​
 = 
(K 
b
​
 ×M) 
2
 +(K 
t
​
 ×T) 
2
 
​
 

T
e
=
(
1.5
×
500
,
000
)
2
+
(
1.0
×
149
,
218.75
)
2
T 
e
​
 = 
(1.5×500,000) 
2
 +(1.0×149,218.75) 
2
 
​
 

T
e
=
750
,
000
2
+
149
,
218.75
2
T 
e
​
 = 
750,000 
2
 +149,218.75 
2
 
​
 

T
e
=
5.625
×
10
11
+
2.2266
×
10
10
T 
e
​
 = 
5.625×10 
11
 +2.2266×10 
10
 
​
 

T
e
=
5.84766
×
10
11
≈
764
,
700.1
 N-mm
T 
e
​
 = 
5.84766×10 
11
 
​
 ≈764,700.1 N-mm
4. Solid Shaft Diameter (
d
d
)
d
=
(
16
×
T
e
π
×
τ
allow
)
1
/
3
d=( 
π×τ 
allow
​
 
16×T 
e
​
 
​
 ) 
1/3
 

d
=
(
16
×
764
,
700.1
π
×
63.0
)
1
/
3
d=( 
π×63.0
16×764,700.1
​
 ) 
1/3
 

d
=
(
12
,
235
,
201.6
197.9203
)
1
/
3
d=( 
197.9203
12,235,201.6
​
 ) 
1/3
 

d
=
(
61
,
818.82
)
1
/
3
≈
39.54
 mm
d=(61,818.82) 
1/3
 ≈39.54 mm
5. Rounding to Standard Size
The minimum allowable standard shaft size rounding up from 
39.54
 mm
39.54 mm
 in the standard list is 40 mm.
code
Code
---

### How to Verify the Tool's Outputs
1. Run the application using `streamlit run app.py`.
2. Input the values from the verification case above in the sidebar.
3. Observe that the calculated minimum diameter displays as **39.54 mm**, and the Recommended Standard Diameter displays as **40 mm**.
4. Check that the compiled PDF report matches these values exactly.