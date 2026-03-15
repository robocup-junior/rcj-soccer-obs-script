# RCJ Soccer OBS Script

An [OBS Studio](https://obsproject.com/) script for live-streaming [RoboCup Junior Soccer](https://junior.robocup.org/) matches. It subscribes to an MQTT broker and automatically updates on-screen text and color sources with real-time match data — team names, scores, game clock, game stage, and team colors.

## How It Works

A match management system publishes game state over MQTT. This OBS script subscribes to those topics and maps each one to an OBS source (text or color), so the overlay updates live without manual intervention.

```
+-------------------------+                  +-------------------------+
|      MQTT Broker        |                  |       OBS Studio        |
|                         |                  |                         |
|  rcj_soccer/field_<N>/  |                  |  Text / Color Sources   |
|                         |                  |                         |
|   team1_name  ----------+----------------->|  Team 1 Name           |
|   team1_score ----------+----------------->|  Team 1 Score          |
|   team1_id    ----------+----------------->|  Team 1 Color          |
|                         |                  |                         |
|   team2_name  ----------+----------------->|  Team 2 Name           |
|   team2_score ----------+----------------->|  Team 2 Score          |
|   team2_id    ----------+----------------->|  Team 2 Color          |
|                         |                  |                         |
|   time        ----------+----------------->|  Match Clock           |
|   game_stage  ----------+----------------->|  Game Stage            |
|                         |                  |                         |
+-------------------------+                  +-------------------------+
```

### MQTT Topics

All topics are published under `rcj_soccer/field_<N>/` where `<N>` is the field number you configure in the script settings. The following sub-topics are subscribed to:

| Topic           | Description                              | OBS Source Type |
|-----------------|------------------------------------------|-----------------|
| `time`          | Current match clock                      | Text            |
| `game_stage`    | Current stage of the game (e.g. half)    | Text            |
| `team1_name`    | Name of Team 1                           | Text            |
| `team1_score`   | Score of Team 1                          | Text            |
| `team1_id`      | Team 1 identifier (`A` or `B`)           | Color           |
| `team2_name`    | Name of Team 2                           | Text            |
| `team2_score`   | Score of Team 2                          | Text            |
| `team2_id`      | Team 2 identifier (`A` or `B`)           | Color           |

Team IDs control the color of a color source: `A` maps to green (`#77FF00`) and `B` maps to pink (`#FF00FF`), matching the physical goal colors used in RCJ Soccer.

## Prerequisites

- **OBS Studio** (version 28+ recommended) with Python scripting support enabled
- **Python 3.6+** (the version bundled with or configured in OBS)
- **[paho-mqtt](https://pypi.org/project/paho-mqtt/)** Python package

## Installation

### 1. Install the MQTT library

```bash
pip install paho-mqtt
```

See the [paho-mqtt documentation](https://pypi.org/project/paho-mqtt/) for more details.

> If OBS uses its own bundled Python, you may need to install into that environment specifically. On some systems you may need the `--break-system-packages` flag.

### 2. Add the script to OBS

1. Open OBS Studio
2. Go to **Tools > Scripts**
3. Click the **+** button and select `rcj_mqtt-subscriber.py`
4. The script settings panel will appear on the right

### 3. Configure MQTT connection

In the script settings, fill in:

| Setting              | Description                                    | Default                                                  |
|----------------------|------------------------------------------------|----------------------------------------------------------|
| **MQTT server hostname** | Hostname of your MQTT broker               | `f2ec5c0344964af6a9b036e32a4f726c.s1.eu.hivemq.cloud`   |
| **MQTT TCP/IP port**     | Broker port                                 | `8883`                                                   |
| **MQTT username**        | Authentication username                     | `RCj_soccer_2025_SubOnly`                                |
| **MQTT password**        | Authentication password                     | `RCj_2025`                                               |
| **TLS/SSL**              | Enable encrypted connection                 | `true`                                                   |
| **Field number**         | Which field to subscribe to (e.g. `1`)      | *(empty)*                                                |

### 4. Set up OBS sources

Create the following sources in your OBS scene. You can name them anything you like — you'll map them in the script settings.

**Text sources** (use *Text (GDI+)* on Windows or *Text (FreeType 2)* on Linux/macOS):
- One for match time
- One for game stage
- One each for team 1 and team 2 names
- One each for team 1 and team 2 scores

**Color sources** (use *Color Source*):
- One for team 1 color indicator
- One for team 2 color indicator

Then in the script settings, use the dropdown menus to map each topic to its corresponding OBS source.

### 5. Connect

Click the **Connect to MQTT** button in the script settings. The status should change to "Connected" and your sources will begin updating in real-time as match data is published.

## Troubleshooting

- **"Failed to connect to MQTT"** — Check that the hostname, port, username, and password are correct. Ensure your network allows outbound connections on the configured port.
- **Sources not updating** — Verify that the field number is set and that the source mappings are correct. Check the OBS script log (**Tools > Scripts > Script Log**) for messages.
- **TLS errors** — The script uses `tls_insecure_set(True)` by default, which skips certificate verification. If your broker requires proper certificate validation, you'll need to modify the `connect_to_mqtt` function.

## Credits

This script was originally created by **[Martin Faltus (mato157)](https://github.com/mato157)** in the [rcj_soccer_obs_script](https://github.com/mato157/rcj_soccer_obs_script) repository.

## License

This project is licensed under the **GNU Affero General Public License v3.0 (AGPLv3)** — see the [LICENSE](LICENSE) file for details.
