import serial
import time
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

def get_force_displacement():
    """ Continuously read force and displacement data from Arduino. """
    try:
        while True:
            data = read_serial()
            if data:
                print(data)
    except KeyboardInterrupt:
        print("\nStopping data stream.")

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
    """ Move stepper by X mm and record force vs. displacement data. """
    print(f"Moving to {x} mm displacement.")
    response = send_command(str(x))
    print(response)

    force_values = []
    displacement_values = []

    print("Recording force and displacement data...")
    while True:
        data = read_serial()
        if data:
            print(data)
            if "Force:" in data and "Displacement:" in data:
                try:
                    parts = data.split(',')
                    force = float(parts[0].split(':')[1].strip().split()[0])
                    displacement = float(parts[1].split(':')[1].strip().split()[0])
                    force_values.append(force)
                    displacement_values.append(displacement)
                except ValueError:
                    pass
        
        if "Moving stepper for X" in data or "Error:" in data:
            break

    # Plot the recorded data
    if force_values and displacement_values:
        plt.figure(figsize=(8, 6))
        plt.plot(displacement_values, force_values, marker='o', linestyle='-')
        plt.xlabel("Displacement (mm)")
        plt.ylabel("Force (N)")
        plt.title("Displacement vs Force")
        plt.grid(True)
        plt.show()

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
