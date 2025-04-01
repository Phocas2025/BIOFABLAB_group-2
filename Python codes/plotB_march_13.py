import serial
import time
import csv

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
    """ Continuously read force and displacement data from Arduino and save to CSV. """
    try:
        with open('force_displacement_data.csv', mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Displacement (mm)", "Force (N)"])  # Write header

            while True:
                data = read_serial()
                if data:
                    print(data)
                    # Assuming data is in the format "displacement,force"
                    try:
                        displacement, force = data.split(',')
                        writer.writerow([displacement, force])
                    except ValueError:
                        print("Error: Invalid data format received from Arduino.")
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
