import serial
import time
import csv
import matplotlib.pyplot as plt

# Set up serial connection (update COM port if needed)
SERIAL_PORT = "COM9"  # Change to your port (e.g., "/dev/ttyUSB0" for Linux)
BAUD_RATE = 9600

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    time.sleep(2)  # Allow time for connection
    print("Connected to Arduino.")
except serial.SerialException:
    print("Error: Could not connect to Arduino.")
    exit()

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

def parse_data(data):
    """
    Parse the data from Arduino into force and displacement values.
    Expected format: "force:0.0N, displacement:0.0 mm"
    Returns: force (float), displacement (float)
    """
    try:
        # Split the data into force and displacement parts
        force_part, displacement_part = data.split(", ")
        
        # Extract numerical values
        force = force_part.split(":")[1].replace("N", "").strip()  # Extract "0.0" from "force:0.0N"
        displacement = displacement_part.split(":")[1].replace("mm", "").strip()  # Extract "0.0" from "displacement:0.0 mm"
        
        # Convert to float
        force_formatted = float(force)
        displacement_formatted = float(displacement)
        
        return force_formatted, displacement_formatted
    except Exception as e:
        print(f"Error parsing data: {e}")
        return None, None

def get_force_displacement():
    """ Continuously read force and displacement data from Arduino, save to CSV, and plot in real-time. """
    # Lists to store data for plotting
    displacements = []
    forces = []

    # Set up the plot
    plt.ion()  # Enable interactive mode
    fig, ax = plt.subplots()
    line, = ax.plot(displacements, forces, 'b-')  # Initial empty line
    ax.set_xlabel("Displacement (mm)")
    ax.set_ylabel("Force (N)")
    ax.set_title("Force vs Displacement")
    ax.grid(True)

    try:
        with open('force_displacement_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Displacement (mm)", "Force (N)"])  # Write header

            while True:
                data = read_serial()
                if data:
                    print(data)
                    # Parse the data into force and displacement
                    force, displacement = parse_data(data)
                    if force is not None and displacement is not None:
                        # Write formatted data to CSV
                        writer.writerow([f"{displacement:.2f}", f"{force:.2f}"])
                        
                        # Append data to lists for plotting
                        displacements.append(displacement)
                        forces.append(force)
                        
                        # Update the plot
                        line.set_xdata(displacements)
                        line.set_ydata(forces)
                        ax.relim()  # Recalculate limits
                        ax.autoscale_view()  # Rescale the view
                        plt.draw()
                        plt.pause(0.01)  # Pause to update the plot
    except KeyboardInterrupt:
        print("\nStopping data stream.")
    finally:
        plt.ioff()  # Turn off interactive mode
        plt.show()  # Keep the plot window open after stopping

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
    """ Move stepper by X mm. """
    print(f"Moving to {x} mm displacement.")
    response = send_command(str(x))
    print(response)

def exit_program():
    """ Gracefully exit the program. """
    send_command("No")
    print("Exiting program...")
    ser.close()

if __name__ == "__main__":
    # Automatically set calibration at startup
    set_calibration()

    while True:
        print("\nOptions:")
        print("1. Read Force & Displacement")
        print("2. Tare Load Cell")
        print("3. Move Stepper (Enter displacement in mm)")
        print("4. Exit")
        
        choice = input("Enter your choice: ")

        if choice == "1":
            get_force_displacement()
        elif choice == "2":
            tare()
        elif choice == "3":
            x = input("Enter displacement in mm: ")
            try:
                move_displacement(float(x))
            except ValueError:
                print("Invalid input! Please enter a number.")
        elif choice == "4":
            exit_program()
            break
        else:
            print("Invalid choice. Try again.")
