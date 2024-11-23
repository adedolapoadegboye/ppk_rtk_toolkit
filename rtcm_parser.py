# File: rtcm_parser.py

import serial
import socket
import datetime
from pyrtcm import RTCMReader

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
        Parse RTCM messages from the stream and log to a file.
        :param output_file: File path to log RTCM messages
        """
        if not self.connection:
            raise Exception("No active connection. Call connect() first.")

        with open(output_file, "w") as log_file:
            log_file.write("Timestamp,Message_Type,Satellite_Count,Correction_Latency\n")
            reader = RTCMReader(self.connection)
            self.is_running = True

            try:
                while self.is_running:
                    raw_data, parsed_message = reader.read()
                    if parsed_message:
                        # Log the data
                        log_file.write(parsed_message)
                        print(parsed_message)
            except Exception as e:
                print(f"Error while parsing: {e}")
            finally:
                self.disconnect()

    def stop(self):
        """Stop the parsing process."""
        self.is_running = False


# Example usage (can be triggered by GUI)
if __name__ == "__main__":
    parser = RTCMParser("COM4", is_serial=True, baudrate=115200)  # Replace with actual port
    parser.connect()
    parser.parse_stream("rtcm_log.csv")