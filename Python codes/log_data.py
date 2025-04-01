import serial
import time
import matplotlib.pyplot as plt

# Initialize serial connection (using software serial port)
arduino = serial.Serial('COM9', 9600, timeout=1)  # Change 'COM9' to your actual port
time.sleep(2)  # Allow time for Arduino to reset

displacement_data = []
force_data = []

# Start reading from the Arduino
try:
    while True:
        if arduino.in_waiting > 0:
            line = arduino.readline().decode('utf-8').strip()
            print(line)  # Print the received data for debugging

            if "Displacement:" in line and "Force:" in line:
                parts = line.split(",")  # Split the string into parts
                displacement = float(parts[0].split(":")[1].strip())
                force = float(parts[1].split(":")[1].strip())

                displacement_data.append(displacement)
                force_data.append(force)

                # Limit the length of the data for better visualization (optional)
                if len(displacement_data) > 100:
                    displacement_data.pop(0)
                    force_data.pop(0)

        # Plot the data
        plt.clf()
        plt.plot(displacement_data, force_data, label='Displacement vs Force')
        plt.xlabel('Displacement (mm)')
        plt.ylabel('Force (N)')
        plt.title('Displacement vs Force')
        plt.legend()
        plt.pause(0.1)

except KeyboardInterrupt:
    print("Data collection stopped.")
    arduino.close()
    plt.show()

