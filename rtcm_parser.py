# File: rtcm_parser.py

import os
import serial
import socket
import datetime
from pyrtcm import RTCMReader

program_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

class RTCMParser:
    def __init__(self, source, is_serial=True, baudrate=9600):
        """
        Initialize RTCMParser for a serial or network stream.
        :param source: COM port for serial or IP:port for TCP/UDP stream
        :param is_serial: True for serial port, False for network stream
        :param baudrate: Baud rate for serial communication (default 9600)
        """
        self.source = source
        self.is_serial = is_serial
        self.baudrate = baudrate
        self.connection = None
        self.is_running = False

    def connect(self):
        """Establish connection to the data source."""
        if self.is_serial:
            self.connection = serial.Serial(self.source, self.baudrate, timeout=1)
        else:
            host, port = self.source.split(":")
            self.connection = socket.create_connection((host, int(port)))

    def disconnect(self):
        """Close the connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def parse_stream(self, output_file):
        """
        Parse RTCM 3.3 messages from the stream and log to a file.
        :param output_file: File path to log RTCM messages
        """
        if not self.connection:
            raise Exception("No active connection. Call connect() first.")

        # Ensure the directory for the output file exists
        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)  # Create the directory if it doesn't exist

        with open(output_file, "w") as log_file:
            reader = RTCMReader(self.connection)
            self.is_running = True

            try:
                while self.is_running:
                    raw_data, parsed_message = reader.read()
                    if parsed_message:
                        # Log the data
                        log_file.write(f"{str(parsed_message)}\n")
                        print(f"Raw Data: {raw_data}")
                        print(f"Parsed Message: {parsed_message}")
            except Exception as e:
                print(f"Error while parsing: {e}")
            finally:
                self.disconnect()

    def stop(self):
        """Stop the parsing process."""
        self.is_running = False


# Example usage (can be triggered by GUI)
if __name__ == "__main__":
    # parser = RTCMParser("COM4", is_serial=True, baudrate=115200)  # Replace with actual port - windows
    parser = RTCMParser("/dev/cu.usbserial-14740", is_serial=True, baudrate=115200)  # Replace with actual port - MacOs
    parser.connect()
    parser.parse_stream(f"./logs/{program_timestamp}_rtcm_log.csv")
