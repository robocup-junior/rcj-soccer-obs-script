#pip install paho-mqtt --break-system-packages

import json
import socket # Just so we can properly handle hostname exceptions
import obspython as obs
import paho.mqtt.client as mqtt
import ssl
import pathlib


# Meta
__version__ = '1.0.0'
__version_info__ = (1, 0, 0)
__license__ = "AGPLv3"
__license_info__ = {
    "AGPLv3": {
        "product": "RoboCup_Soccer_subscribe_mqtt_",
        "users": 0, # 0 being unlimited
        "customer": "Unsupported",
        "version": __version__,
        "license_format": "1.0",
    }
}
__author__ = 'Martin Faltus'

__doc__ = """\
RoboCup Soccer subscriber for MQTT topics for live streaming
"""



last_payload = ""


# Default values for MQTT the configurable options:
MQTT_HOST = "f2ec5c0344964af6a9b036e32a4f726c.s1.eu.hivemq.cloud" # Hostname of your MQTT server
MQTT_USER = "RCj_soccer_2025_SubOnly"
MQTT_PW = "RCj_2025"
MQTT_PORT = 8883 # Default MQTT port is 1883
MQTT_TOPIC = ""
#SOURCE_NAME = ""
MQTT_TLS = True # Use TLS/SSL by default
MQTT_STATUS = "Disconnected" # Default status message

#### MQTT TOPICS ####
# Variable for MQTT topics for team names and scores
MQTT_BASE_TOPIC = "rcj_soccer/field_"
MQTT_TOPIC_TIME = "time"
MQTT_TOPIC_STAGE = "game_stage"

MQTT_TOPIC_TEAM1_ID = "team1_id"
MQTT_TOPIC_TEAM1_NAME = "team1_name"
MQTT_TOPIC_TEAM1_SCORE = "team1_score"

MQTT_TOPIC_TEAM2_ID = "team2_id"
MQTT_TOPIC_TEAM2_NAME = "team2_name"
MQTT_TOPIC_TEAM2_SCORE = "team2_score"


#### SOURCES ####
# Variable for source for team names and scores
SOURCE_TEAM1_ID = ""
SOURCE_TEAM1_NAME = ""
SOURCE_TEAM1_SCORE = ""

SOURCE_TEAM2_ID = ""
SOURCE_TEAM2_NAME = ""
SOURCE_TEAM2_SCORE = ""

# Variable fo source for time and game stage
SOURCE_TIME = ""
SOURCE_STAGE = ""


# MQTT Event Functions
def on_mqtt_connect(client, userdata, flags, rc):
    """
    Called when the MQTT client is connected from the server.  Just prints a
    message indicating we connected successfully.
    """
    print("MQTT connection successful")
    global MQTT_STATUS
    MQTT_STATUS = "Connected"

    set_config()

def on_mqtt_disconnect(client, userdata, rc):
    """
    Called when the MQTT client gets disconnected.  Just logs a message about it
    (we'll auto-reconnect inside of update_status()).
    """
    print("MQTT disconnected.  Reason: {}".format(str(rc)))

    global MQTT_STATUS
    MQTT_STATUS = "Disconnected"


def on_mqtt_message(client, userdata, message):
    """
    Handles MQTT messages that have been subscribed to and updates the correct source.
    """
    global last_payload

    topic = pathlib.PurePosixPath(message.topic)
    payload = str(message.payload.decode("utf-8"))
    print(message.topic + ": " + payload)

    if payload != last_payload:
        source_name = None

        # Match the topic to the corresponding source
        if topic.name == MQTT_TOPIC_TIME:
            source_name = SOURCE_TIME
        elif topic.name == MQTT_TOPIC_STAGE:
            source_name = SOURCE_STAGE
        elif topic.name == MQTT_TOPIC_TEAM1_NAME:
            source_name = SOURCE_TEAM1_NAME
        elif topic.name == MQTT_TOPIC_TEAM1_SCORE:
            source_name = SOURCE_TEAM1_SCORE
        elif topic.name == MQTT_TOPIC_TEAM1_ID:
            source_name = SOURCE_TEAM1_ID
        elif topic.name == MQTT_TOPIC_TEAM2_NAME:
            source_name = SOURCE_TEAM2_NAME
        elif topic.name == MQTT_TOPIC_TEAM2_SCORE:
            source_name = SOURCE_TEAM2_SCORE
        elif topic.name == MQTT_TOPIC_TEAM2_ID:
            source_name = SOURCE_TEAM2_ID
        else:
            print("No source found for topic: " + topic.name)
            return

        # Update the source if a match is found
        if source_name:
            source = obs.obs_get_source_by_name(source_name)
            #print("Updating source: " + source_name)
            if source is not None:
                settings = obs.obs_data_create()

                if topic.name == MQTT_TOPIC_TEAM1_ID or topic.name == MQTT_TOPIC_TEAM2_ID:
                    # For team IDs, we change color of source based on the payload
                    if payload == 'A':
                        color = int("FF00FF77", 16)  # Greenish color
                    elif payload == 'B':
                        color = int("FFFF00FF", 16)  # Pinkish color

                    obs.obs_data_set_int(settings, "color", color)
                    obs.obs_data_set_int(settings, "color1", color)
                    obs.obs_data_set_int(settings, "color2", color)
                else:
                    # For other topics, we set the text
                    obs.obs_data_set_string(settings, "text", payload)

                # # Change the color of the text
                # color = int("FFFF0000", 16)# | 0x5F000000  # Adjusted to BBGGRR format (0xAABBGGRR)
                # obs.obs_data_set_int(settings, "color1", color)  # Use "color1" for text color
                # obs.obs_data_set_int(settings, "color2", color)  # Use "color2" for text color
                # print("Setting text to: " + payload + " with color: " + hex(color))

                obs.obs_source_update(source, settings)
                obs.obs_data_release(settings)
                obs.obs_source_release(source)

        #last_payload = payload

# OBS Script Function Exports
def script_description():
    return __doc__ # We wrote a nice docstring...  Might as well use it!

def script_load(settings):
    """
    Just prints a message indicating that the script was loaded successfully.
    """
    print("MQTT script loaded.")

def script_unload():
    """
    Publishes a final status message indicating OBS is off
    (so your MQTT sensor doesn't get stuck thinking you're
    recording/streaming forever) and calls `CLIENT.disconnect()`.
    """
    if CLIENT.is_connected():
        CLIENT.disconnect()
    CLIENT.loop_stop()
##############################################################
def script_defaults(settings):
    """
    Sets up our default settings in the OBS Scripts interface.
    """
    obs.obs_data_set_default_string(settings, "mqtt_host", MQTT_HOST)
    obs.obs_data_set_default_string(settings, "mqtt_user", MQTT_USER)
    obs.obs_data_set_default_string(settings, "mqtt_pw", MQTT_PW)
    obs.obs_data_set_default_string(settings, "mqtt_topic", MQTT_TOPIC)
    obs.obs_data_set_default_int(settings, "mqtt_port", MQTT_PORT)
    obs.obs_data_set_default_bool(settings, "mqtt_tls", MQTT_TLS)

def script_properties():
    """
    Makes this script's settings configurable via OBS's Scripts GUI.
    """
    global MQTT_HOST, MQTT_USER, MQTT_PW, MQTT_PORT, MQTT_TOPIC, MQTT_TLS, MQTT_STATUS

    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "mqtt_host", "MQTT server hostname", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "mqtt_port", "MQTT TCP/IP port", MQTT_PORT, 65535, 1)
    obs.obs_properties_add_text(props, "mqtt_user", "MQTT username", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "mqtt_pw", "MQTT password", obs.OBS_TEXT_PASSWORD)
    obs.obs_properties_add_bool(props, "mqtt_tls", "TLS/SSL")
    obs.obs_properties_add_text(props, "mqtt_topic", "Field number",obs.OBS_TEXT_DEFAULT)

    # Add a button to connect to the MQTT server
    # Add a button to connect to the MQTT server
    obs.obs_properties_add_button(props, "connect_button", "Connect to MQTT", connect_to_mqtt)

    # Add a text field to display the current connection state
    obs.obs_properties_add_text(props, "connection_state", "Status: ", obs.OBS_TEXT_INFO)
    #obs.obs_property_set_enabled(connection_state, False)  # Make it read-only


    obs.obs_properties_add_text(props, "spacer1", "", obs.OBS_TEXT_INFO)
    obs.obs_properties_add_text(props, "spacer2", "", obs.OBS_TEXT_INFO)
    # Source list for time
    p_time = obs.obs_properties_add_list(props, "source_time", "Time Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Source list for game stage
    p_stage = obs.obs_properties_add_list(props, "source_stage", "Game Stage Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Source list for team1 name
    p_team1_name = obs.obs_properties_add_list(props, "source_team1_name", "Team 1 Name Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Source list for team1 score
    p_team1_score = obs.obs_properties_add_list(props, "source_team1_score", "Team 1 Score Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Source list for team1 id
    p_team1_id = obs.obs_properties_add_list(props, "source_team1_id", "Team 1 Color", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Source list for team2 name
    p_team2_name = obs.obs_properties_add_list(props, "source_team2_name", "Team 2 Name Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Source list for team2 score
    p_team2_score = obs.obs_properties_add_list(props, "source_team2_score", "Team 2 Score Source", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Source list for team2 id
    p_team2_id = obs.obs_properties_add_list(props, "source_team2_id", "Team 2 Color", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)

    # Populate sources for each list
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if source_id == "text_gdiplus" or source_id == "text_ft2_source" or source_id == "color_source":
                name = obs.obs_source_get_name(source)
                obs.obs_property_list_add_string(p_time, name, name)
                obs.obs_property_list_add_string(p_stage, name, name)
                obs.obs_property_list_add_string(p_team1_name, name, name)
                obs.obs_property_list_add_string(p_team1_score, name, name)
                obs.obs_property_list_add_string(p_team1_id, name, name)
                obs.obs_property_list_add_string(p_team2_name, name, name)
                obs.obs_property_list_add_string(p_team2_score, name, name)
                obs.obs_property_list_add_string(p_team2_id, name, name)
    obs.source_list_release(sources)

    return props

def script_update(settings):
    """
    Applies any changes made to the MQTT settings in the OBS Scripts GUI then
    reconnects the MQTT client.
    """
    # Apply the new settings
    global MQTT_HOST
    global MQTT_USER
    global MQTT_PW
    global MQTT_PORT
    global MQTT_TOPIC
    global MQTT_TLS
    global MQTT_STATUS
    global SOURCE_TIME, SOURCE_STAGE
    global SOURCE_TEAM1_ID, SOURCE_TEAM1_NAME, SOURCE_TEAM1_SCORE
    global SOURCE_TEAM2_ID, SOURCE_TEAM2_NAME, SOURCE_TEAM2_SCORE

    mqtt_host = obs.obs_data_get_string(settings, "mqtt_host")
    if mqtt_host != MQTT_HOST:
        MQTT_HOST = mqtt_host
    mqtt_user = obs.obs_data_get_string(settings, "mqtt_user")
    if mqtt_user != MQTT_USER:
        MQTT_USER = mqtt_user
    mqtt_pw = obs.obs_data_get_string(settings, "mqtt_pw")
    if mqtt_pw != MQTT_PW:
        MQTT_PW = mqtt_pw
    mqtt_port = obs.obs_data_get_int(settings, "mqtt_port")
    if mqtt_port != MQTT_PORT:
        MQTT_PORT = mqtt_port
    mqtt_topic = obs.obs_data_get_string(settings, "mqtt_topic")
    if mqtt_topic != MQTT_TOPIC:
        MQTT_TOPIC = mqtt_topic
    mqtt_tls = obs.obs_data_get_bool(settings, "mqtt_tls")
    if mqtt_tls != MQTT_TLS:
        MQTT_TLS = mqtt_tls

    # SOURSES
    source_time = obs.obs_data_get_string(settings, "source_time")
    if source_time != SOURCE_TIME:
        SOURCE_TIME = source_time

    source_stage = obs.obs_data_get_string(settings, "source_stage")
    if source_stage != SOURCE_STAGE:
        SOURCE_STAGE = source_stage

    source_team1_id = obs.obs_data_get_string(settings, "source_team1_id")
    if source_team1_id != SOURCE_TEAM1_ID:
        SOURCE_TEAM1_ID = source_team1_id

    source_team1_name = obs.obs_data_get_string(settings, "source_team1_name")
    if source_team1_name != SOURCE_TEAM1_NAME:
        SOURCE_TEAM1_NAME = source_team1_name

    source_team1_score = obs.obs_data_get_string(settings, "source_team1_score")
    if source_team1_score != SOURCE_TEAM1_SCORE:
        SOURCE_TEAM1_SCORE = source_team1_score

    source_team2_id = obs.obs_data_get_string(settings, "source_team2_id")
    if source_team2_id != SOURCE_TEAM2_ID:
        SOURCE_TEAM2_ID = source_team2_id

    source_team2_name = obs.obs_data_get_string(settings, "source_team2_name")
    if source_team2_name != SOURCE_TEAM2_NAME:
        SOURCE_TEAM2_NAME = source_team2_name

    source_team2_score = obs.obs_data_get_string(settings, "source_team2_score")
    if source_team2_score != SOURCE_TEAM2_SCORE:
        SOURCE_TEAM2_SCORE = source_team2_score

    # Update the connection state dynamically
    # obs.obs_data_set_string(settings, "connection_state", MQTT_STATUS)
    # print("status: " + MQTT_STATUS)


    # # Disconnect (if connected) and reconnect the MQTT client
    # CLIENT.disconnect()
    # try:
    #     if MQTT_PW != "" and MQTT_USER != "":
    #         CLIENT.username_pw_set(MQTT_USER, password=MQTT_PW)
    #     if MQTT_TLS:
    #         CLIENT.tls_set()
    #         CLIENT.tls_insecure_set(True)

    #     CLIENT.connect_async(MQTT_HOST, MQTT_PORT, 60)

    # except (socket.gaierror, ConnectionRefusedError) as e:
    #     print("NOTE: Got a socket issue: %s" % e)
    #     pass # Ignore it for now

    # CLIENT.loop_start()


def set_config():
    if MQTT_TOPIC != "":
        CLIENT.subscribe(MQTT_BASE_TOPIC + MQTT_TOPIC + "/" + MQTT_TOPIC_TIME)
        CLIENT.subscribe(MQTT_BASE_TOPIC + MQTT_TOPIC + "/" + MQTT_TOPIC_STAGE)
        CLIENT.subscribe(MQTT_BASE_TOPIC + MQTT_TOPIC + "/" + MQTT_TOPIC_TEAM1_ID)
        CLIENT.subscribe(MQTT_BASE_TOPIC + MQTT_TOPIC + "/" + MQTT_TOPIC_TEAM1_NAME)
        CLIENT.subscribe(MQTT_BASE_TOPIC + MQTT_TOPIC + "/" + MQTT_TOPIC_TEAM1_SCORE)
        CLIENT.subscribe(MQTT_BASE_TOPIC + MQTT_TOPIC + "/" + MQTT_TOPIC_TEAM2_ID)
        CLIENT.subscribe(MQTT_BASE_TOPIC + MQTT_TOPIC + "/" + MQTT_TOPIC_TEAM2_NAME)
        CLIENT.subscribe(MQTT_BASE_TOPIC + MQTT_TOPIC + "/" + MQTT_TOPIC_TEAM2_SCORE)

        print("Subscribed to topics with base rcj_soccer/field_" + MQTT_TOPIC + "/")

# Using a global MQTT client variable to keep things simple:
CLIENT = mqtt.Client()
CLIENT.on_connect = on_mqtt_connect
CLIENT.on_disconnect = on_mqtt_disconnect
CLIENT.on_message = on_mqtt_message


def connect_to_mqtt(props, prop):
    """
    Handles the 'Connect to MQTT' button click event.
    """

    # Disconnect (if connected) and reconnect the MQTT client
    CLIENT.disconnect()

    try:
        if MQTT_PW != "" and MQTT_USER != "":
            CLIENT.username_pw_set(MQTT_USER, password=MQTT_PW)
        if MQTT_TLS:
            if CLIENT._ssl_context is None:  # Check if TLS is already set
                CLIENT.tls_set()
                CLIENT.tls_insecure_set(True)

        CLIENT.connect_async(MQTT_HOST, MQTT_PORT, 60)
        CLIENT.loop_start()
        print("MQTT connection initiated.")

    except (socket.gaierror, ConnectionRefusedError) as e:
        print("Failed to connect to MQTT: %s" % e)
