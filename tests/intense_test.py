import json
import time
import paho.mqtt.client as mqtt

BROKER = "broker.hivemq.com"
PORT = 1883
TOPIC = "iot/smarttank/actions"

client = mqtt.Client()
client.connect(BROKER, PORT, 60)

commands = [
    "Push",
    "Pull",
    "Rotate",
    "Lift",
    "Left",
    "Right"
]

print("Starting Stress Test...")

count = 0

for i in range(5000):  # Send 1000 commands

    payload = {
        "command": commands[i % len(commands)],
        "command_id": str(i + 1)
    }

    client.publish(
        TOPIC,
        json.dumps(payload)
    )

    count += 1

    print(f"Sent {count}: {payload}")

    time.sleep(0.5)  # 50 ms between commands

print(f"\nStress Test Complete. Total Messages Sent: {count}")

client.disconnect()