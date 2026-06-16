from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO
import paho.mqtt.client as mqtt
from threading import Thread
import time
import json
import csv
import random
import os
import uuid  # new 10/06/26

# ================= MQTT TOPICS =================

TOPIC_PREFIX = "iot/smarttank"

ACTION_TOPIC = f"{TOPIC_PREFIX}/actions"
STATUS_TOPIC = f"{TOPIC_PREFIX}/status" 
ACK_TOPIC = f"{TOPIC_PREFIX}/system_ack"

# ================= FLASK =================

app = Flask(
    __name__,
    template_folder="../templates",
    static_folder="../static"
)

socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode="threading"
)

# ================= DATA =================

latest_data = {

    "water":0,

    "command":"Neutral",

    "system":"OFFLINE",

    "up":"OFF",

    "down":"OFF",

    "left":"OFF",

    "right":"OFF",

    "ack":"WAITING...",

    "mode":"MANUAL"

}

# new 10/06/26 
pending_commands = {} 




mode = "MANUAL"

# old commads list


commands = [

    "Rotate",
    "Down",
    "Left",
    "Right",

    "Rotate_Left",
    "Rotate_Right",

    "Push",
    "Pull",

    "Neutral"

]

command_map = {

    "Lift": "Rotate",
    "Drop": "Down",

    "Push": "Push",
    "Pull": "Pull",

    "Left": "Left",
    "Right": "Right",

    "Neutral": "Neutral"

}

last_seen = 0

# 10/06/26 chnages  adding uuid 


mqtt_client = mqtt.Client()

# ================= CSV =================

if not os.path.exists(

    "command_logs.csv"

):

    with open(

        "command_logs.csv",

        "w",

        newline=""

    ) as f:

        writer = csv.writer(f)

        writer.writerow([

            "TIME",

            "COMMAND",

            "STATUS"

        ])

def log_command(command, status):

    with open(

        "command_logs.csv",

        "a",

        newline=""

    ) as f:

        writer = csv.writer(f)

        writer.writerow([

            time.strftime(

                "%H:%M:%S"

            ),

            command,
         # new
            status

        ])

# ================= MQTT =================

def on_connect(

    client,

    userdata,

    flags,

    rc

):

    print(

        "MQTT Connected:",

        rc

    )

    client.subscribe(

        STATUS_TOPIC

    )

    client.subscribe(

        ACK_TOPIC

    )

def on_message(

    client,

    userdata,

    msg

):

    global last_seen

    last_seen = time.time()

    payload = msg.payload.decode()

    print(

        msg.topic,

        payload

    )

    # -------- STATUS --------

    if msg.topic == STATUS_TOPIC:

        try:

            data = json.loads(
                payload
            )

            latest_data.update(
                data
            )

        except:

            print(
                "JSON ERROR"
            )

    # -------- ACK --------

    elif msg.topic == ACK_TOPIC:

        latest_data["ack"] = payload

        try:

            ack_data = json.loads(
                payload
            )

            command_id = ack_data.get(
                "command_id"
            )

            if command_id in pending_commands:

                pending_commands[
                    command_id
                ]["status"] = "SUCCESS"
                log_command( 
                    pending_commands[command_id]["command"],
                    "SUCCESS"
                )
                print(
                    f"ACK Received: {command_id}"
                )

                del pending_commands[
                    command_id
                ]

        except Exception as e:

            print(
                "ACK Parse Error:",
                e
            )

    latest_data["system"] = "ONLINE"

    socketio.emit(

        "mqtt_data",

        latest_data

    )



mqtt_client.on_connect = on_connect

mqtt_client.on_message = on_message

mqtt_client.connect(

    "broker.hivemq.com",

    1883,

    60

)

mqtt_client.loop_start()

# ================= WATCHDOG =================

def watchdog():

    global last_seen

    while True:

        if (

            last_seen and

            time.time()-last_seen > 20

        ):

            latest_data["system"] = "OFFLINE"

        time.sleep(5)

Thread(

    target=watchdog,

    daemon=True

).start()

# new -----14  10


# new ------
def retry_monitor():

    while True:

        current_time = time.time()

        for command_id in list(
            pending_commands.keys()
        ):

            cmd_info = pending_commands[
                command_id
            ]

            elapsed = (
                current_time -
                cmd_info["timestamp"]
            )

            if elapsed > 3:

                if cmd_info[
                    "attempts"
                ] >= 3:

                    print(
                        f"FAILED: "
                        f"{cmd_info['command']}"
                    )
                    log_command(
                        cmd_info["command"],
                        "FAILED"
                    )
                    del pending_commands[
                        command_id
                    ]

                else:

                    payload = {

                        "command_id":
                        command_id,

                        "command":
                        cmd_info["command"]

                    }

                    mqtt_client.publish(

                        ACTION_TOPIC,

                        json.dumps(payload)

                    )

                    cmd_info[
                        "attempts"
                    ] += 1

                    cmd_info[
                        "timestamp"
                    ] = time.time()

                    print(

                        f"Retry "

                        f"{cmd_info['attempts']} "

                        f"for "

                        f"{cmd_info['command']}"

                    )

        time.sleep(1)

Thread(
    target=retry_monitor,
    daemon=True
).start()


    
# new 10/06/26  random commands with uuid and pending command tracking
def random_commands():

    global mode

    while True:

        if mode == "RANDOM":

            cmd = random.choice(commands)

            command_id = str(uuid.uuid4())

            payload = {
                "command_id": command_id,
                "command": cmd
            }

            pending_commands[command_id] = {
                "command": cmd,
                "status": "WAITING",
                "attempts": 1,
                "timestamp": time.time()

            }

            mqtt_client.publish(
                ACTION_TOPIC,
                json.dumps(payload)
            )

            print(
                f"Sent Random Command: {cmd} | {command_id}"
            )

            log_command(
                cmd,
                "SENT"
            )

        time.sleep(3)    

#=======================================================

Thread(

    target=random_commands,

    daemon=True

).start()


# new 10/06/26 loading json commands with uuid and pending command tracking
def load_json_commands():

    with open("json.txt", "r") as f:
        data = json.load(f)

    for item in data:

        if item["Is_Actionable"]:

            cmd = command_map.get(
                item["Command"],
                "Neutral"
            )

            # Generate Unique Command ID
            command_id = str(uuid.uuid4())

            payload = {
                "command_id": command_id,
                "command": cmd
            }

            # Store Pending Command
            pending_commands[command_id] = {
                "command": cmd,
                "status": "WAITING",
                "attempts": 1,
                "timestamp": time.time()

            }

            # Publish Command
            result = mqtt_client.publish(
                ACTION_TOPIC,
                json.dumps(payload)
            )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print("publish success")

                print(
                    f"Sent JSON Command: {cmd} | ID: {command_id}"
                )

                log_command(
                    f"{cmd} ({command_id})",
                    "SENT"
                )

            else:
                print("publish Failed")
                print(
                    f"Failed To Send: {cmd}"
                )

            time.sleep(2)

# ================= ROUTES =================

@app.route("/")

def home():

    return render_template(

        "index.html"

    )

@app.route("/status")

def status():

    return jsonify(

        latest_data

    )


# new 10/06/26

@app.route("/device/<command>")
def control(command):

    command_id = str(uuid.uuid4())

    payload = {
        "command_id": command_id,
        "command": command
    }

    pending_commands[command_id] = {
        "command": command,
        "status": "WAITING",
        "attempts": 1,
        "timestamp": time.time()
    }

    result = mqtt_client.publish(
        ACTION_TOPIC,
        json.dumps(payload)
    )

    if result.rc == mqtt.MQTT_ERR_SUCCESS:

        log_command(
            f"{command} ({command_id})",
            "SENT"
        )

        return jsonify({
            "success": True,
            "command_id": command_id
        })

    return jsonify({
        "success": False
    })



# new modes  09

@app.route("/mode/<newmode>")
def change_mode(newmode):

    global mode

    mode = newmode.upper()

    latest_data["mode"] = mode

    socketio.emit(
        "mqtt_data",
        latest_data
    )

    return jsonify({

        "mode":mode

    })



# new modes 09 
@app.route("/play_json")
def play_json():

    global mode

    mode = "JSON PLAY"

    latest_data["mode"] = mode

    socketio.emit(
        "mqtt_data",
        latest_data
    )

    Thread(
        target=load_json_commands,
        daemon=True
    ).start()

    return jsonify({

        "status":"JSON Playback Started"

    })
# 12/06/26

@app.route("/ble")
def ble():
    return render_template("ble_dashboard.html")



# ================= RUN =================

if __name__ == "__main__":

    socketio.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
        allow_unsafe_werkzeug=True
    )
