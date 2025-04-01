import serial
import time
import threading

# Serial port configuration
SERIAL_PORT = 'COM9'  # Replace with your Arduino's serial port
BAUD_RATE = 115200

# Global flag to control the data reading thread
running = True

# Function to continuously read data from the Arduino
def read_serial_data(ser):
    while running:
        if ser.in_waiting > 0:
            line = ser.readline().decode().strip()
            if line:  # Print only non-empty lines
                print(line)  # Print the data in real-time

# Function to send a command to the Arduino
def send_command(ser, command):
    try:
        # Send the command to Arduino
        ser.write(f"{command}\n".encode())
        print(f"Sent command: {command}")
    except Exception as e:
        print(f"Error: {e}")

# Function to send displacement value to Arduino
def send_displacement(ser, displacement):
    try:
        # Send the displacement value to Arduino
        ser.write(f"{displacement}\n".encode())
        print(f"Sent displacement: {displacement} mm")
    except Exception as e:
        print(f"Error: {e}")

# Function to display the menu
def display_menu():
    print("\n--- Menu ---")
    print("1. Tare the load cell")
    print("2. Input displacement")
    print("3. Exit program")

# Main loop
if __name__ == "__main__":
    try:
        # Open serial connection
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # Wait for the connection to establish

        # Start a thread to continuously read data from the Arduino
        data_thread = threading.Thread(target=read_serial_data, args=(ser,))
        data_thread.start()

        while True:
            # Display the menu
            display_menu()

            # Get user choice
            choice = input("Enter your choice (1, 2, or 3): ")

            if choice == "1":
                # Tare the load cell
                send_command(ser, "t")
                print("Load cell tared.")
            elif choice == "2":
                # Input displacement
                try:
                    displacement = float(input("Enter displacement in mm (positive or negative): "))
                    send_displacement(ser, displacement)
                except ValueError:
                    print("Invalid input. Please enter a valid number.")
            elif choice == "3":
                # Exit the program
                print("Exiting program...")
                running = False  # Stop the data reading thread
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
    except serial.SerialException as e:
        print(f"Serial port error: {e}")
    finally:
        # Ensure the serial connection is closed
        if 'ser' in locals() and ser.is_open:
            ser.close()
        if 'data_thread' in locals():
            data_thread.join()  # Wait for the data thread to finish
