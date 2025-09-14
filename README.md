# Online Unit Converter

A Python web application for unit conversion. Users can enter an expression (e.g., `G * c/ (km/s)^2 * (mass of sun) / kpc`) and select the output unit system (e.g., cgs, SI) to get the converted result. Uses the `astropy` library.

## How to Run

1. Install dependencies:
   ```bash
   pip install flask astropy
   ```
2. Run the app:
   ```bash
   python app.py
   ```
3. Open your browser at http://127.0.0.1:5000
