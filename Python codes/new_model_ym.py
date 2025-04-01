import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load the force-displacement data
data = pd.read_csv("force_displacement_data_1.csv")
displacement = data["Displacement (mm)"].values
force = data["Force (N)"].values

# Convert displacement to meters for SI consistency
displacement = displacement / 1000  # mm to meters

# Define the Kelvin-Voigt model for viscoelastic behavior
def kelvin_voigt(delta, E, eta):
    velocity = np.gradient(delta)  # Calculate velocity (rate of displacement)
    return E * delta + eta * velocity

# Fit the model to the data
popt, _ = curve_fit(kelvin_voigt, displacement, force, p0=[1e5, 1e-3])

# Extract the parameters
E = popt[0]  # Elastic modulus (Young's modulus)
eta = popt[1]  # Viscous damping coefficient

print(f"Estimated Young's Modulus (E) = {E:.3f} Pa")
print(f"Estimated Viscous Damping Coefficient (η) = {eta:.3f} Ns/m")

# Plot the results
plt.scatter(displacement, force, label="Experimental Data", color="b")
plt.plot(displacement, kelvin_voigt(displacement, *popt), label="Fitted Curve (Kelvin-Voigt Model)", color="r")
plt.xlabel("Displacement (m)")
plt.ylabel("Force (N)")
plt.title("Force vs Displacement with Viscoelastic Model")
plt.legend()
plt.grid(True)
plt.show()
