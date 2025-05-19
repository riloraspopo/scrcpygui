# GuiScrcpy

A graphical user interface for scrcpy that allows you to easily discover, connect to, and control Android devices on your network.

![GuiScrcpy Screenshot](screenshot.png)

## Features

- **Network Scanning**: Automatically scans your local network for Android devices with ADB over TCP/IP enabled (port 5555)
- **Easy Connection**: Connect to any discovered device with a single click
- **Screen Control**: Toggle your Android device's screen on/off directly from the application
- **Multi-threaded Scanning**: Uses 100 threads for fast network scanning
- **User-friendly Interface**: Simple and intuitive GUI built with Tkinter

## Requirements

- Python 3.6+
- scrcpy
- xdotool (for screen toggling functionality)
- Android device with:
  - USB debugging enabled
  - ADB over TCP/IP enabled

## Installation

1. Clone this repository:

   ```
   git clone https://github.com/yourusername/GuiScrcpy.git
   cd GuiScrcpy
   ```

2. Make sure you have scrcpy installed:

   ```
   sudo apt install scrcpy
   ```

3. Install xdotool (for screen control functionality):
   ```
   sudo apt install xdotool
   ```

## Usage

1. Run the application:

   ```
   python guiscrcpy.py
   ```

2. Click "Scan Network" to find Android devices on your network with port 5555 open

3. Select a device from the list and click "Connect & Mirror" to launch scrcpy

4. Use the "Screen Off" button to toggle your device's screen on/off:
   - When the screen is on, clicking turns it off (Alt+O)
   - When the screen is off, clicking turns it on (Alt+Shift+O)

## Setting Up Your Android Device

1. Enable Developer Options:

   - Go to Settings → About Phone
   - Tap "Build Number" 7 times
   - Go back to Settings to find Developer Options

2. Enable USB Debugging:

   - Go to Settings → Developer Options
   - Enable "USB Debugging"

3. Connect your device via USB and enable ADB over TCP/IP:

   ```
   adb tcpip 5555
   ```

4. Disconnect USB and run GuiScrcpy to find your device on the network

## Keyboard Shortcuts

When connected through scrcpy, you can use these keyboard shortcuts:

- **Alt+O**: Turn off the device screen
- **Alt+Shift+O**: Turn on the device screen
- (All standard scrcpy shortcuts also work)

## License

[MIT License](LICENSE)

## Acknowledgements

- [scrcpy](https://github.com/Genymobile/scrcpy) - The amazing tool for displaying and controlling Android devices
- [xdotool](https://github.com/jordansissel/xdotool) - Command-line tool to simulate keyboard input and window management

---

## Future Development: Android-to-Android Remote Control

We're working on a complete mobile solution that will allow you to control one Android device from another Android device, without needing a computer:

### Key Features of Upcoming Android App

- **Direct Device-to-Device Control**: Control one Android device from another over WiFi
- **Low Latency Streaming**: View the target device's screen in near real-time
- **Touch Translation**: Control the target device with natural touch gestures
- **Secure Connection**: Encrypted communication between devices
- **No Root Required**: Uses Android's built-in APIs for screen capture and input

For more details, see our [Android Development Plan](AndroidCompanion.md).

---

Made with ❤️ by [Your Name]
