# Custom Encryption and Decryption System

## Overview
This repository contains an implementation of a custom encryption and decryption system that ensures secure communication using the MQTT protocol. The system utilizes a dynamic matrix generated from a password and the current datetime to encrypt and decrypt messages.

## Encryption Process
1. **Padding:** Messages are padded to ensure they fit into 16-byte blocks.
2. **Fixed Shuffling:** The characters in each block are shuffled based on predefined indices.
3. **Substitution:** Each character in the block is substituted using an S-box.
4. **Column Replacement:** Columns of the 4x4 matrix are replaced according to a fixed pattern.
5. **XOR Operation:** The matrix is XORed with a dynamically generated matrix based on the password and current datetime.
6. **Hexadecimal Conversion:** The resulting encrypted matrix is converted to a hexadecimal string.

## Decryption Process
1. **Hexadecimal Conversion:** The hexadecimal string is converted back to a matrix.
2. **XOR Operation:** The matrix is XORed with the dynamic matrix generated from the password and encryption datetime.
3. **Column Replacement:** Columns are replaced back to their original positions.
4. **Inverse Substitution:** Each value in the matrix is substituted back using the inverse S-box.
5. **Unshuffling:** The characters are unshuffled to their original order.
6. **Padding Removal:** Padding is removed to retrieve the original message.

## MQTT Communication
* **Publisher:** Encrypts the message and publishes it to an MQTT broker.
* **Subscriber:** Subscribes to the broker, receives the encrypted message, and decrypts it.

# Setting Up MQTT
To use the MQTT protocol for publishing and subscribing to messages, you'll need to install an MQTT broker and set it up. The most commonly used broker is Mosquitto. Here's how you can install and set it up on different platforms.

## Installing Mosquitto MQTT Broker
### On Ubuntu/Debian
*Update package list:*

```bash
sudo apt update
```

#### Install Mosquitto:

```bash
sudo apt install -y mosquitto mosquitto-clients
```

#### Enable and start Mosquitto service:

```bash
sudo systemctl enable mosquitto
sudo systemctl start mosquitto
```

#### Verify Mosquitto status:

```bash
sudo systemctl status mosquitto
```

### On Windows
Download Mosquitto: Go to the Mosquitto download page and download the Windows installer.

Install Mosquitto: Run the installer and follow the on-screen instructions.

Run Mosquitto: You can start Mosquitto by running mosquitto.exe from the installation directory.

# Configuring Mosquitto
The default configuration file for Mosquitto is typically found at /etc/mosquitto/mosquitto.conf on Linux or C:\Program Files\mosquitto\mosquitto.conf on Windows. You can edit this file to customize your broker settings.

### Basic Configuration
To enable remote access and add basic security, you can modify the configuration file as follows:

### Open the configuration file in a text editor:

```bash
sudo nano /etc/mosquitto/mosquitto.conf
```

### Add the following lines to enable password file authentication:

conf
allow_anonymous false
password_file /etc/mosquitto/passwd

### Create a password file and add a user:

```bash
sudo mosquitto_passwd -c /etc/mosquitto/passwd yourusername
```

### Restart Mosquitto to apply changes:

```bash
sudo systemctl restart mosquitto
```

## How to Use

### Encryption
1. Run the encryption script.
2. Enter the password.
3. Input the message to encrypt and publish.
4. The encrypted message is published to the MQTT broker.

### Decryption
1. Run the decryption script.
2. Enter the password when prompted.
3. The script will automatically subscribe to the MQTT broker, receive the encrypted message, and decrypt it.

## Dependencies
* numpy
* paho-mqtt
* hashlib
* datetime
* getpass

## Running the Scripts

To run the encryption script:
```bash
python encrypter_MQTT.py
```

To run the decryption script:
```bash
python decrypter_MQTT.py
```

Ensure that the MQTT broker is running and accessible at the specified address and port.

## Notes
•	The system requires the password and the datetime of encryption to successfully decrypt the message.
•	The MQTT broker address and port need to be correctly set in the scripts.

## License
This project is licensed under the MIT License.

