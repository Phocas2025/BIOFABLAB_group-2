import serial
import time
import matplotlib.pyplot as plt

# Initialize serial connection
arduino = serial.Serial('COM9', 9600, timeout=1)  # Change 'COM9' to your actual port
time.sleep(2)  # Allow time for Arduino to reset

displacement_data = []
force_data = []

# Start reading from the Arduino
try:
    plt.ion()  # Interactive mode for live updating plot
    fig, ax = plt.subplots()

    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            print(line)  # Print the received data for debugging

            if "Displacement:" in line and "Force:" in line:
                parts = line.split(",")  # Split the string into parts
                try:
                    displacement = float(parts[0].split(":")[1].strip())
                    force = float(parts[1].split(":")[1].strip())

                    displacement_data.append(displacement)
                    force_data.append(force)

                    # Limit the length of the data for better visualization (optional)
                    if len(displacement_data) > 100:
                        displacement_data.pop(0)
                        force_data.pop(0)

                    # Update plot
                    ax.clear()
                    ax.plot(displacement_data, force_data, label='Displacement vs Force', color='b', marker='o')
                    ax.set_xlabel('Displacement (mm)')
                    ax.set_ylabel('Force (N)')
                    ax.set_title('Displacement vs Force')
                    ax.legend()
                    plt.pause(0.1)

                except ValueError:
                    print("Error parsing data:", line)

except KeyboardInterrupt:
    print("Data collection stopped.")
    arduino.close()
    plt.ioff()
    plt.show()
