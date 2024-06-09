import numpy as np
import hashlib
import datetime
import paho.mqtt.client as mqtt
import getpass

# Define the S-box (16x16) and its inverse
S_BOX = np.array([
    [0x63, 0x7c, 0x77, 0x7b, 0xf2, 0x6b, 0x6f, 0xc5, 0x30, 0x01, 0x67, 0x2b, 0xfe, 0xd7, 0xab, 0x76],
    [0xca, 0x82, 0xc9, 0x7d, 0xfa, 0x59, 0x47, 0xf0, 0xad, 0xd4, 0xa2, 0xaf, 0x9c, 0xa4, 0x72, 0xc0],
    [0xb7, 0xfd, 0x93, 0x26, 0x36, 0x3f, 0xf7, 0xcc, 0x34, 0xa5, 0xe5, 0xf1, 0x71, 0xd8, 0x31, 0x15],
    [0x04, 0xc7, 0x23, 0xc3, 0x18, 0x96, 0x05, 0x9a, 0x07, 0x12, 0x80, 0xe2, 0xeb, 0x27, 0xb2, 0x75],
    [0x09, 0x83, 0x2c, 0x1a, 0x1b, 0x6e, 0x5a, 0xa0, 0x52, 0x3b, 0xd6, 0xb3, 0x29, 0xe3, 0x2f, 0x84],
    [0x53, 0xd1, 0x00, 0xed, 0x20, 0xfc, 0xb1, 0x5b, 0x6a, 0xcb, 0xbe, 0x39, 0x4a, 0x4c, 0x58, 0xcf],
    [0xd0, 0xef, 0xaa, 0xfb, 0x43, 0x4d, 0x33, 0x85, 0x45, 0xf9, 0x02, 0x7f, 0x50, 0x3c, 0x9f, 0xa8],
    [0x51, 0xa3, 0x40, 0x8f, 0x92, 0x9d, 0x38, 0xf5, 0xbc, 0xb6, 0xda, 0x21, 0x10, 0xff, 0xf3, 0xd2],
    [0xcd, 0x0c, 0x13, 0xec, 0x5f, 0x97, 0x44, 0x17, 0xc4, 0xa7, 0x7e, 0x3d, 0x64, 0x5d, 0x19, 0x73],
    [0x60, 0x81, 0x4f, 0xdc, 0x22, 0x2a, 0x90, 0x88, 0x46, 0xee, 0xb8, 0x14, 0xde, 0x5e, 0x0b, 0xdb],
    [0xe0, 0x32, 0x3a, 0x0a, 0x49, 0x06, 0x24, 0x5c, 0xc2, 0xd3, 0xac, 0x62, 0x91, 0x95, 0xe4, 0x79],
    [0xe7, 0xc8, 0x37, 0x6d, 0x8d, 0xd5, 0x4e, 0xa9, 0x6c, 0x56, 0xf4, 0xea, 0x65, 0x7a, 0xae, 0x08],
    [0xba, 0x78, 0x25, 0x2e, 0x1c, 0xa6, 0xb4, 0xc6, 0xe8, 0xdd, 0x74, 0x1f, 0x4b, 0xbd, 0x8b, 0x8a],
    [0x70, 0x3e, 0xb5, 0x66, 0x48, 0x03, 0xf6, 0x0e, 0x61, 0x35, 0x57, 0xb9, 0x86, 0xc1, 0x1d, 0x9e],
    [0xe1, 0xf8, 0x98, 0x11, 0x69, 0xd9, 0x8e, 0x94, 0x9b, 0x1e, 0x87, 0xe9, 0xce, 0x55, 0x28, 0xdf],
    [0x8c, 0xa1, 0x89, 0x0d, 0xbf, 0xe6, 0x42, 0x68, 0x41, 0x99, 0x2d, 0x0f, 0xb0, 0x54, 0xbb, 0x16]
], dtype=np.uint8)

# Inverse S-box (16x16)
INV_S_BOX = np.zeros_like(S_BOX)
for i in range(16):
    for j in range(16):
        INV_S_BOX[S_BOX[i][j] >> 4, S_BOX[i][j] & 0x0F] = (i << 4) | j

# Fixed shuffled indices
SHUFFLED_INDICES = [3, 0, 2, 1, 7, 4, 6, 5, 11, 8, 10, 9, 15, 12, 14, 13]
UNSHUFFLED_INDICES = [SHUFFLED_INDICES.index(i) for i in range(16)]

def inverse_substitute(byte):
    row = byte >> 4  # Take the first half (high bits) as the row
    col = byte & 0x0F  # Take the second half (low bits) as the column
    return INV_S_BOX[row][col]

def unshuffle_string(s):
    return ''.join(s[i] for i in UNSHUFFLED_INDICES)

def remove_padding(padded_string):
    print("Cipher Text:", padded_string)
    original_length = int(padded_string[-3:])  # Extracting the original length
    print("Text:", original_length)
    return padded_string[:original_length]

def generate_dynamic_matrix(password, current_datetime):
    # Generate SHA-256 hashes of the password and the date-time string
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    datetime_hash = hashlib.sha256(current_datetime.encode()).hexdigest()

    # Convert hashes to integers and perform XOR
    xor_result = int(password_hash, 16) ^ int(datetime_hash, 16)

    # Convert the XOR result to a hex string
    xor_hex = hex(xor_result)[2:].zfill(64)  # Ensure it's 64 characters long

    # Convert the hex string to Unicode values
    unicode_values = [ord(char) for char in xor_hex]

    # Select 16 values based on a specific pattern to create the new matrix
    selected_values = [unicode_values[i % len(unicode_values)] for i in range(16)]

    # Convert selected values to a 4x4 matrix
    dynamic_matrix = np.array(selected_values).reshape(4, 4)

    return dynamic_matrix

def decrypt_hex_string(hex_string, password, encryption_datetime):
    # Generate the dynamic matrix based on the password and the encryption datetime
    HARDCODED_MATRIX = generate_dynamic_matrix(password, encryption_datetime)

    encrypted_bytes = bytes.fromhex(hex_string)
    decrypted_message = []

    # Process each 16-byte block
    for i in range(0, len(encrypted_bytes), 16):
        block = np.frombuffer(encrypted_bytes[i:i+16], dtype=np.uint8).reshape(4, 4)

        # XOR operation with the dynamic matrix
        xor_result = block ^ HARDCODED_MATRIX

        # Replace columns back to original positions
        temp_matrix = xor_result.copy()
        xor_result[:, 2] = temp_matrix[:, 0]
        xor_result[:, 3] = temp_matrix[:, 1]
        xor_result[:, 0] = temp_matrix[:, 2]
        xor_result[:, 1] = temp_matrix[:, 3]

        # Reverse the S-box substitution
        for i in range(4):
            for j in range(4):
                xor_result[i, j] = inverse_substitute(xor_result[i, j])

        # Flatten the matrix and convert to characters
        flat_values = xor_result.flatten()
        decrypted_chunk = ''.join(chr(value) for value in flat_values)

        # Unshuffle the string
        unshuffled_chunk = unshuffle_string(decrypted_chunk)
        decrypted_message.append(unshuffled_chunk)

    decrypted_message = ''.join(decrypted_message)
    return remove_padding(decrypted_message)  # Remove padding spaces

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("topic/test")

def on_message(client, userdata, msg):
    password = getpass.getpass("Enter the password: ")
    print("Received message: " + str(msg.payload.decode()))
    encrypted_hex_string = msg.payload.decode()
    current_datetime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
    print("Decryption DateTime:", current_datetime)
    
    # Extract the encryption datetime from the user
    #encryption_datetime = input("Enter the encryption datetime (YYYY-MM-DD HH:MM): ")
    
    # Compare current datetime (ignoring seconds) to the provided datetime
    #if encryption_datetime.split(":")[0:2] != current_datetime.split(":")[0:2]:
    #    print("Cipher is protected")
    #    return
    
    decrypted_message = decrypt_hex_string(encrypted_hex_string, password, current_datetime)
    print("Decrypted Message:", decrypted_message + "\n")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

broker_address = "192.168.43.218"  # Replace with your broker's address
port = 1883  # Default MQTT port

client.connect(broker_address, port, 60)

client.loop_forever()


