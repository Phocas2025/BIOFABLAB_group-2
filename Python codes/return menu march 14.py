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
        force_part, displacement_part = data.split(", ")
        force = float(force_part.split(":")[1].replace("N", "").strip())
        displacement = -float(displacement_part.split(":")[1].replace("mm", "").strip())
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
    """ Move stepper by X mm. Reverse the direction logic. """
    reversed_x = -x
    print(f"Moving to {x} mm displacement (reversed direction: {reversed_x} mm).")
    response = send_command(str(reversed_x))
    print(response)

def move_and_read(x):
    """ Move stepper by X mm, read force and displacement, and auto-tare after start. """
    print(f"Moving to {x} mm displacement with a 3-second delay before starting.")
    time.sleep(3)

    displacements = []
    forces = []

    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot(displacements, forces, 'b-')
    ax.set_xlabel("Displacement (mm)")
    ax.set_ylabel("Force (N)")
    ax.set_title("Force vs Displacement")
    ax.grid(True)

    try:
        with open('force_displacement_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Displacement (mm)", "Force (N)"])

            move_displacement(x)
            time.sleep(0.5)
            tare()

            while True:
                data = read_serial()
                if data:
                    force, displacement = parse_data(data)
                    if force is not None and displacement is not None:
                        print(f"Force: {force:.2f} N, Displacement: {displacement:.2f} mm")
                        writer.writerow([f"{displacement:.2f}", f"{force:.2f}"])
                        displacements.append(displacement)
                        forces.append(force)
                        line.set_xdata(displacements)
                        line.set_ydata(forces)
                        ax.relim()
                        ax.autoscale_view()
                        plt.draw()
                        plt.pause(0.01)
                        if abs(displacement - x) < 0.01:
                            print("Movement finished. Returning to menu.")
                            break
    except KeyboardInterrupt:
        print("\nStopping data stream.")
    finally:
        plt.ioff()
        plt.show()

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
            try:
                x = float(input("Enter displacement in mm: "))
                move_and_read(x)
            except ValueError:
                print("Invalid input! Please enter a number.")
        elif choice == "3":
            exit_program()
            break
        else:
            print("Invalid choice. Try again.")
