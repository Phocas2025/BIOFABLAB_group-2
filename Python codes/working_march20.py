import serial
import time
import csv
import matplotlib.pyplot as plt
import itertools  # For cycling through colors

# Set up serial connection
SERIAL_PORT = "COM9"  # Change if needed
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)
    print("Connected to Arduino.")
except serial.SerialException:
    print("Error: Could not connect to Arduino.")
    exit()

# Track total displacement
total_displacement = 0.0  

def read_serial():
    """ Read data from Arduino and return it as a string. """
    try:
        line = ser.readline().decode("utf-8").strip()
        return line
    except Exception as e:
        print(f"Error reading serial: {e}")
        return None

def send_command(cmd):
    """ Send a command to the Arduino and wait for a response. """
    ser.write((cmd + "\n").encode())
    time.sleep(0.1)
    return read_serial()

def clear_serial_buffer():
    """ Clear the serial buffer to ensure fresh data is read. """
    ser.reset_input_buffer()

def parse_data(data):
    """ Parse the data from Arduino into force and displacement values. """
    try:
        force_part, displacement_part = data.split(", ")
        force = float(force_part.split(":")[1].replace("N", "").strip())
        displacement = float(displacement_part.split(":")[1].replace("mm", "").strip())
        return force, displacement
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None, None

def tare():
    """ Tare the load cell. """
    print("Taring load cell...")
    response = send_command("t")
    print(response)

def set_calibration():
    """ Set calibration factor to 45000. """
    CALIBRATION_FACTOR = 45000
    print(f"Setting calibration factor to {CALIBRATION_FACTOR}...")
    response = send_command(f"cal {CALIBRATION_FACTOR}")
    print(response)

def move_displacement(x):
    """ Move stepper by X mm (relative movement). """
    global total_displacement

    new_target = x  # **Use relative movement, NOT absolute positions**

    print(f"Moving stepper by {new_target:.2f} mm {'clockwise' if x > 0 else 'counterclockwise'}")
    response = send_command(str(new_target))  # Send relative move command
    print(response)

    total_displacement += x  # Accumulate the relative movement

# ** Set up persistent plot **
plt.ion()
fig, ax = plt.subplots()
ax.set_xlabel("Displacement (mm)")
ax.set_ylabel("Force (N)")
ax.set_title("Force vs Displacement")
ax.grid(True)

# ** Cycle through colors for different plots **
color_cycle = itertools.cycle(["b", "g", "r", "c", "m", "y", "k"])  

def move_and_read(x):
    """ Move stepper by X mm (relative movement) and acquire force-displacement data. """
    print(f"Moving by {x} mm displacement with a 3-second delay before starting.")
    time.sleep(3)

    # ** Reset Data Lists ** 
    displacements = []
    forces = []

    # ** Clear Serial Buffer ** 
    clear_serial_buffer()

    # ** Get Next Color for the New Curve ** 
    color = next(color_cycle)

    # ** Start Movement ** 
    move_displacement(x)

    # ** Wait for Motor to Complete Movement **
    while True:
        data = read_serial()
        if data and "END" in data:  # Detect the END signal
            print("Motor movement completed.")
            break
        elif data:
            force, displacement = parse_data(data)
            if force is not None and displacement is not None:
                print(f"Force: {force:.2f} N, Displacement: {displacement:.2f} mm")

                # Write to file
                with open('force_displacement_data.csv', mode='a', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow([f"{displacement:.2f}", f"{force:.2f}"])

                # ** Append Data for Plotting ** 
                displacements.append(displacement)
                forces.append(force)

                # ** Plot New Data Without Clearing Old Data ** 
                ax.plot(displacements, forces, linestyle='-', marker='', color=color, label=f"Move {x} mm" if len(displacements) == 1 else "")
                ax.legend()  # Update legend
                plt.draw()
                plt.pause(0.01)

    # ** Return to Menu **
    return

def exit_program():
    """ Gracefully exit the program and save the plot. """
    print("Saving final plot before exiting...")
    plt.savefig("force_displacement_plot.png", dpi=300, bbox_inches='tight')  # Save plot as PNG
    print("Plot saved as 'force_displacement_plot.png'.")
    send_command("No")
    print("Exiting program...")
    ser.close()
    plt.close()  # Close the plot window

if __name__ == "__main__":
    set_calibration()

    while True:
        print("\nOptions:")
        print("1. Tare Load Cell")
        print("2. Move Stepper (Enter displacement in mm, relative move)")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            tare()
        elif choice == "2":
            x = input("Enter displacement in mm (relative move): ")
            try:
                move_and_read(float(x))
            except ValueError:
                print("Invalid input! Please enter a number.")
        elif choice == "3":
            exit_program()
            break
        else:
            print("Invalid choice. Try again.")
