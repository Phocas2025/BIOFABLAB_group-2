import serial
import time
import csv
import matplotlib.pyplot as plt

# Set up serial connection
SERIAL_PORT = "COM9"  # Change if needed
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
    """ Move stepper by X mm (reversed direction). """
    reversed_x = -x
    print(f"Moving to {x} mm displacement (reversed direction: {reversed_x} mm).")
    response = send_command(str(reversed_x))
    print(response)

def move_and_read(x):
    """ Move stepper by X mm and acquire force-displacement data. """
    print(f"Moving to {x} mm displacement with a 3-second delay before starting.")
    time.sleep(3)

    # ** Reset Data Lists **
    displacements = []
    forces = []

    # ** Clear Serial Buffer **
    clear_serial_buffer()

    # ** Close Previous Plot (If Exists) **
    plt.close('all')

    # ** Set Up Plot **
    plt.ion()  
    fig, ax = plt.subplots()
    line, = ax.plot([], [], 'b-')  
    ax.set_xlabel("Displacement (mm)")
    ax.set_ylabel("Force (N)")
    ax.set_title("Force vs Displacement")
    ax.grid(True)

    # ** Start Movement **
    move_displacement(x)

    # ** Tare 0.5 Seconds After Movement Starts **
    time.sleep(0.5)
    tare()

    # ** Track Previous Displacement to Detect Stopping **
    prev_displacement = None
    stable_readings = 0  # Counts how many times the displacement remains unchanged

    try:
        with open('force_displacement_data.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            if file.tell() == 0:
                writer.writerow(["Displacement (mm)", "Force (N)"])

            while True:
                data = read_serial()
                if data:
                    force, displacement = parse_data(data)
                    if force is not None and displacement is not None:
                        print(f"Force: {force:.2f} N, Displacement: {displacement:.2f} mm")
                        writer.writerow([f"{displacement:.2f}", f"{force:.2f}"])

                        # ** Append Data for Plotting **
                        displacements.append(displacement)
                        forces.append(force)

                        # ** Update Plot **
                        line.set_xdata(displacements)
                        line.set_ydata(forces)
                        ax.relim()
                        ax.autoscale_view()
                        plt.draw()
                        plt.pause(0.01)

                        # ** Stop if Displacement is Reached and Stays Stable **
                        if prev_displacement is not None and abs(displacement - prev_displacement) < 0.01:
                            stable_readings += 1
                        else:
                            stable_readings = 0  # Reset if displacement changes

                        prev_displacement = displacement

                        # ** Exit After 5 Consecutive Stable Readings **
                        if stable_readings >= 5:
                            print("Movement finished. Stopping data collection.")
                            break
    except KeyboardInterrupt:
        print("\nStopping data stream.")
    finally:
        plt.ioff()  
        plt.show(block=False)  # Keep the final plot visible

def exit_program():
    """ Gracefully exit the program. """
    send_command("No")
    print("Exiting program...")
    ser.close()

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
