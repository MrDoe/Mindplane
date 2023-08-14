# Mindplane - EEG Controlled Arcade Game

![Mindplane Logo](mindplane_logo.png)

## Overview

Mindplane is an arcade game that lets you control a plane's position using EEG signals from the Muse 2 headband. Fly the plane through a star-filled sky while navigating obstacles and collecting stars to increase your score. The game provides an immersive experience by translating your brain activity into real-time gameplay.

## Requirements

- Python 3.6+
- [muselsl library](https://github.com/alexandrebarachant/muse-lsl) running in the background (`muselsl stream`)
- Muse 2 headband
- Pygame library (`pip install pygame`)
- Paho MQTT library (`pip install paho-mqtt`)

## Setup

1. Connect your Muse 2 headband and make sure the [muselsl library](https://github.com/alexandrebarachant/muse-lsl) is running in the background by executing the command `muselsl stream`.

2. Clone or download the Mindplane repository to your local machine.

3. Install the required Python libraries using the following command: pip install pygame paho-mqtt

4. Run the game by executing the `mindplane.py` script:
python mindplane.py


## How to Play

- Use your brain's EEG signals to control the plane's position.
- Calibrate the game by following the on-screen instructions to determine the minimum and maximum EEG signal values.
- Avoid obstacles and collect stars to increase your score.
- Use the "Up" arrow key to increase acceleration and the "Down" arrow key to decrease acceleration.
- The game runs for a total of 120 seconds. Try to achieve the highest score before time runs out!

## Credits

Developed by Christoph Döllinger (christoph.d@posteo.de).

## Acknowledgments

- [muselsl library](https://github.com/alexandrebarachant/muse-lsl) by Alexandre Barachant
- Star and plane images by [OpenGameArt.org](https://opengameart.org/)

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

Mindplane is an experimental project intended for entertainment and educational purposes. The EEG signals and their interpretation may vary, and the game's performance might be affected by factors such as signal quality and individual brain activity. Please use the game responsibly and consider your health and comfort while playing.
