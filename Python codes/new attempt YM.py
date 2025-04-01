import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

# Load the force-displacement data
data = pd.read_csv("force_displacement_data_5_02.csv")
displacement = data.iloc[:, 0].values * 1e-3  # Convert mm to meters
force = data.iloc[:, 1].values  # Force remains in Newtons

# Choose the model
indenter_type = input("Enter indenter type (sphere/flat): ").strip().lower()

if indenter_type == "sphere":
    R = float(input("Enter sphere radius (mm): ")) * 1e-3  # Convert mm to meters
    nu = 0.5  # Poisson's ratio for hydrogel

    # Define the modified Hertzian function with all 4 parameters: E*, delta0, d, and F0
    def modified_hertzian(delta, E_star, delta0, d, F0):
        return (4/3) * E_star * np.sqrt(R) * (np.clip(delta - delta0, 0, None) ** d) + F0

    # Ask the user for initial guesses
    E_star_guess = float(input("Enter initial guess for E* (Pa): "))
    delta0_guess = float(input("Enter initial guess for delta0 (m): "))
    d_guess = float(input("Enter initial guess for d (1-2): "))
    F0_guess = float(input("Enter initial guess for F0 (N): "))

    initial_guess = [E_star_guess, delta0_guess, d_guess, F0_guess]

    # Define bounds for parameters: E_star, delta0, and F0 can have realistic ranges
    lower_bounds = [0, 0, 1, -np.inf]  # E_star ≥ 0, delta0 ≥ 0, d ≥ 1, F0 can be any value
    upper_bounds = [np.inf, np.inf, 2, np.inf]  # d ≤ 2, F0 ≤ some realistic value

    # Perform curve fitting with bounds
    popt, _ = curve_fit(modified_hertzian, displacement, force, p0=initial_guess,
                        bounds=(lower_bounds, upper_bounds))

    # Extract optimized parameters
    E_star, delta0, d, F0 = popt
    E = E_star / (1 - nu**2)  # Corrected Young’s modulus (Pa)

    # Print results
    print("\nEstimated Parameters:")
    print(f"E* = {E_star:.3f} Pa")
    print(f"delta0 = {delta0:.6f} m")
    print(f"d = {d:.3f}")
    print(f"F0 = {F0:.3f} N")
    print(f"Corrected Young's Modulus (E) = {E:.3f} Pa")

    # Plot results with the fitted data
    plt.scatter(displacement * 1e3, force, label="Experimental Data", color="b", alpha=0.6)  # Convert back to mm for plotting
    plt.plot(displacement * 1e3, modified_hertzian(displacement, *popt), label="Fitted Curve", color="r")
    
    # Annotation for Young's modulus value on the graph
    plt.text(0.1 * max(displacement) * 1e3, 0.9 * max(force), f"E = {E:.3f} Pa", fontsize=12, color="red")

    plt.xlabel("Displacement (mm)")
    plt.ylabel("Force (N)")
    plt.title(f"Young's Modulus Estimation (Sphere, R={R * 1e3} mm)")

    plt.legend()
    plt.grid(True)
    plt.show()

else:
    print("Invalid indenter type. Currently, only 'sphere' is supported.")
