import json
import time
import paho.mqtt.client as mqtt

# MQTT Broker
BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "iot/smarttank/actions"

# Create client
client = mqtt.Client()

print("Connecting to MQTT Broker...")
client.connect(BROKER, PORT, 60)

command_id = 1

while True:
    print("\nAvailable Commands:")
    print("1. Push   (Light ON)")
    print("2. Pull   (Light OFF)")
    print("3. Rotate (Fan ON)")
    print("4. Lift   (Fan OFF)")
    print("5. Left   (Pump ON)")
    print("6. Right  (Pump OFF)")
    print("7. Exit")

    choice = input("Enter command: ")

    command_map = {
        "1": "Push",
        "2": "Pull",
        "3": "Rotate",
        "4": "Lift",
        "5": "Left",
        "6": "Right"
    }

    if choice == "7":
        break

    if choice not in command_map:
        print("Invalid Choice")
        continue

    payload = {
        "command": command_map[choice],
        "command_id": str(command_id)
    }

    client.publish(
        TOPIC,
        json.dumps(payload)
    )

    print(f"Published: {payload}")

    command_id += 1
    time.sleep(1)

client.disconnect()