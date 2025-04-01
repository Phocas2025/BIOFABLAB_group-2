import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load the force-displacement data
data = pd.read_csv("force_displacement_data_1.csv")
displacement = data.iloc[:, 0].values  # First column: Displacement (mm)
force = data.iloc[:, 1].values  # Second column: Force (N)

# Choose the model
indenter_type = input("Enter indenter type (sphere/flat): ").strip().lower()

if indenter_type == "sphere":
    R = float(input("Enter sphere radius (mm): "))  # Radius of spherical indenter
    nu = 0.5  # Poisson's ratio for hydrogel

    # Define the Hertzian function: F = (4/3) * E* * sqrt(R) * delta^(3/2)
    def hertzian(delta, E):
        return (4/3) * E * np.sqrt(R) * (delta ** 1.5)
    
    # Fit force vs. displacement^(3/2)
    popt, _ = curve_fit(hertzian, displacement, force)
    E_star = popt[0]
    E = E_star / (1 - nu**2) * 1e6  # Correct for Poisson ratio

    print(f"Estimated Young's Modulus (E) = {E:.3f} Pa")

    # Plot results
    plt.scatter(displacement, force, label="Experimental Data", color="b")
    plt.plot(displacement, hertzian(displacement, *popt), label="Fitted Curve", color="r")
    plt.xlabel("Displacement (mm)")
    plt.ylabel("Force (N)")
    plt.title(f"Young's Modulus Estimation (Sphere, R={R} mm)")
    plt.legend()
    plt.grid(True)
    plt.show()

elif indenter_type == "flat":
    a = float(input("Enter indenter radius (mm): "))  # Radius of flat punch
    nu = 0.5  # Poisson's ratio

    # Define the flat punch model: F = (2 E a / π(1-ν²)) * δ
    def flat_punch(delta, E):
        return (2 * E * a) / (np.pi * (1 - nu**2)) * delta
    
    # Fit force vs. displacement
    popt, _ = curve_fit(flat_punch, displacement, force)
    E = popt[0]

    print(f"Estimated Young's Modulus (E) = {E:.3f} Pa")

    # Plot results
    plt.scatter(displacement, force, label="Experimental Data", color="b")
    plt.plot(displacement, flat_punch(displacement, *popt), label="Fitted Curve", color="r")
    plt.xlabel("Displacement (mm)")
    plt.ylabel("Force (N)")
    plt.title(f"Young's Modulus Estimation (Flat Punch, a={a} mm)")
    plt.legend()
    plt.grid(True)
    plt.show()

else:
    print("Invalid indenter type. Choose 'sphere' or 'flat'.")

# Define the Hertzian contact model
def hertzian_model(h, E_star):
    R = 0.5e-3  # Radius of the spherical indenter in meters (0.5 mm)
    return (4/3) * E_star * np.sqrt(R) * h**(3/2)

# Load the experimental data from a CSV file
# Assuming the CSV file has two columns: 'Displacement' (mm) in the first column and 'Force' (N) in the second column
data = pd.read_csv('force_displacement_data_1.csv', header=None)  # No header in the CSV file
displacement_mm = data[0].values  # Displacement in millimeters (mm)
force = data[1].values  # Force in Newtons (N)

# Convert displacement from millimeters to meters
displacement_m = displacement_mm * 1e-3  # 1 mm = 1e-3 m

# Print the experimental data
print("Experimental Data:")
print("Force (N) | Displacement (m)")
for f, d in zip(force, displacement_m):
    print(f"{f:.6f}  | {d:.6f}")

# Initial guess for E_star
# E_star is the effective Young's modulus
initial_guess = [1e3]  # Adjust this value based on your experiment

# Fit the data to the Hertzian model
params, covariance = curve_fit(hertzian_model, displacement_m, force, p0=initial_guess)
E_star_fit = params[0]

# Calculate the Young's modulus E
nu = 0.5  # Poisson's ratio for the hydrogel
E_fit = E_star_fit * (1 - nu**2)

# Print the results
print(f"\nFitted Effective Young's Modulus (E*): {E_star_fit} Pa")
print(f"Calculated Young's Modulus (E): {E_fit} Pa")

# Plot the experimental data and the fitted curve
plt.scatter(displacement_m, force, label='Experimental Data')
plt.plot(displacement_m, hertzian_model(displacement_m, E_star_fit), label='Fitted Hertzian Model', color='red')
plt.xlabel('Displacement (m)')
plt.ylabel('Force (N)')
plt.legend()
plt.title('Hertzian Contact Model Fit (R = 0.5 mm)')
plt.show()
