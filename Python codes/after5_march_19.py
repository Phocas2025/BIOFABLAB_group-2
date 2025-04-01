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
        displacement = -float(displacement_part.split(":")[1].replace("mm", "").strip())  # Reverse sign
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
    """ Move stepper by X mm (corrected direction). """
    print(f"Moving to {x} mm displacement.")
    
    # The direction of movement is reversed to align with the Arduino code:
    # Positive input will move the motor clockwise (opposite of original behavior in your script).
    reversed_x = x  # No sign change here, we want to match Arduino behavior directly.

    # Send the command to Arduino to move the motor
    response = send_command(str(reversed_x))
    print(response)


# ** Set up persistent plot **
plt.ion()  
fig, ax = plt.subplots()
ax.set_xlabel("Displacement (mm)")
ax.set_ylabel("Force (N)")
ax.set_title("Force vs Displacement")
ax.grid(True)

# ** Cycle through colors for different plots **
color_cycle = itertools.cycle(["b", "g", "r", "c", "m", "y", "k"])  

# ** Initialize cumulative displacement **
cumulative_displacement = 0.0

def move_and_read(x):
    """ Move stepper by X mm and acquire force-displacement data. """
    global cumulative_displacement  # Use the global cumulative displacement

    print(f"Moving to {x} mm displacement with a 3-second delay before starting.")
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

    # ** Tare 0.5 Seconds After Movement Starts ** 
    time.sleep(0.5)
    tare()

    # ** Track Previous Displacement to Detect Stopping ** 
    prev_displacement = None
    stable_readings = 0  

    motor_stopped = False  # Flag to track if motor has stopped
    stop_time = None  # Time when motor stopped
    post_movement_duration = 2.0  # Collect data for 2 seconds after motor stops

    try:
        with open('force_displacement_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Displacement (mm)", "Force (N)"])

            while True:
                data = read_serial()
                if data:
                    # Check if motor has stopped
                    if "Motor Stopped" in data:
                        motor_stopped = True
                        stop_time = time.time()  # Record the time when motor stopped
                        print("Motor has stopped. Collecting final data...")

                    # Parse force and displacement data
                    if "Force:" in data and "Displacement:" in data:
                        force, displacement = parse_data(data)
                        if force is not None and displacement is not None:
                            # ** Adjust displacement to be cumulative **
                            adjusted_displacement = cumulative_displacement + displacement

                            # ** Print displacement correctly (positive or negative as needed) **
                            print(f"Force: {force:.2f} N, Displacement: {adjusted_displacement:.2f} mm")

                            # Write to file
                            writer.writerow([f"{adjusted_displacement:.2f}", f"{force:.2f}"])

                            # ** Append Data for Plotting ** 
                            displacements.append(adjusted_displacement)
                            forces.append(force)

                            # ** Plot New Data Without Clearing Old Data ** 
                            ax.plot(displacements, forces, linestyle='-', marker='', color=color, label=f"Move {x} mm" if len(displacements) == 1 else "")
                            ax.legend()  # Update legend
                            plt.draw()
                            plt.pause(0.01)

                            # ** Stop if Displacement is Reached and Stays Stable ** 
                            if prev_displacement is not None and abs(displacement - prev_displacement) < 0.01:
                                stable_readings += 1
                            else:
                                stable_readings = 0  

                            prev_displacement = displacement

                            # ** Exit After 5 Consecutive Stable Readings ** 
                            if stable_readings >= 20:
                                print("Movement finished. Stopping data collection.")
                                cumulative_displacement = adjusted_displacement  # Update cumulative displacement
                                break

                # Stop data collection after motor has stopped and post-movement duration has passed
                if motor_stopped and (time.time() - stop_time >= post_movement_duration):
                    print("Data collection complete.")
                    break
    except KeyboardInterrupt:
        print("\nStopping data stream.")
    finally:
        plt.show(block=False)  # Keep the plot alive


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
        print("2. Move Stepper (Enter displacement in mm)")
        print("3. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            tare()
        elif choice == "2":
            x = input("Enter displacement in mm: ")
            try:
                move_and_read(float(x))
            except ValueError:
                print("Invalid input! Please enter a number.")
        elif choice == "3":
            exit_program()
            break
        else:
            print("Invalid choice. Try again.")
