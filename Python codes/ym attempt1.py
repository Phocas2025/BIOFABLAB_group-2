import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load the force-displacement data
data = pd.read_csv("force_displacement_data_1_03.csv")
displacement = data.iloc[:, 0].values * 1e-3  # Convert mm to meters
force = data.iloc[:, 1].values  # Force remains in Newtons

# Choose the model
indenter_type = input("Enter indenter type (sphere/flat): ").strip().lower()

if indenter_type == "sphere":
    R = float(input("Enter sphere radius (mm): ")) * 1e-3  # Convert mm to meters
    nu = 0.5  # Poisson's ratio for hydrogel

    # Define the Hertzian function: F = (4/3) * E* * sqrt(R) * delta^(3/2)
    def hertzian(delta, E):
        return (4/3) * E * np.sqrt(R) * (delta ** 1.5)
    
    # Fit force vs. displacement^(3/2)
    popt, _ = curve_fit(hertzian, displacement, force)
    E_star = popt[0]
    E = E_star / (1 - nu**2)  # Correct for Poisson ratio (Pa)

    print(f"Estimated Young's Modulus (E) = {E:.3f} Pa")

    # Plot results
    plt.scatter(displacement * 1e3, force, label="Experimental Data", color="b")  # Convert back to mm for plotting
    plt.plot(displacement * 1e3, hertzian(displacement, *popt), label="Fitted Curve", color="r")
    plt.xlabel("Displacement (mm)")
    plt.ylabel("Force (N)")
    plt.title(f"Young's Modulus Estimation (Sphere, R={R * 1e3} mm)")
    plt.legend()
    plt.grid(True)
    plt.text(0.1 * max(displacement) * 1e3, 0.9 * max(force), f"E = {E:.3f} Pa", fontsize=12, color="red")
    plt.show()

elif indenter_type == "flat":
    a = float(input("Enter indenter radius (mm): ")) * 1e-3  # Convert mm to meters
    nu = 0.5  # Poisson's ratio

    # Define the flat punch model: F = (2 E a / π(1-ν²)) * δ
    def flat_punch(delta, E):
        return (2 * E * a) / (np.pi * (1 - nu**2)) * delta
    
    # Fit force vs. displacement
    popt, _ = curve_fit(flat_punch, displacement, force)
    E = popt[0]

    print(f"Estimated Young's Modulus (E) = {E:.3f} Pa")

    # Plot results
    plt.scatter(displacement * 1e3, force, label="Experimental Data", color="b")  # Convert back to mm for plotting
    plt.plot(displacement * 1e3, flat_punch(displacement, *popt), label="Fitted Curve", color="r")
    plt.xlabel("Displacement (mm)")
    plt.ylabel("Force (N)")
    plt.title(f"Young's Modulus Estimation (Flat Punch, a={a * 1e3} mm)")
    plt.legend()
    plt.grid(True)
    plt.text(0.1 * max(displacement) * 1e3, 0.9 * max(force), f"E = {E:.3f} Pa", fontsize=12, color="red")
    plt.show()

else:
    print("Invalid indenter type. Choose 'sphere' or 'flat'.")
