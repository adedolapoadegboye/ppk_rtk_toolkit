# File: main_gui.py

import tkinter as tk
from tkinter import filedialog, messagebox
import serial.tools.list_ports
from tkinter import ttk
import threading
from rtcm_parser import RTCMParser
import datetime


program_timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")


# Main PPK-RTK Toolkit Class
class PPKRTKToolkit:
    def __init__(self, root):
        self.local_tcp_udp_input = None
        self.local_usb_dropdown = None
        self.local_usb_ports = None
        self.station_stream_input = None
        self.local_stream_input = None
        self.stream_input = None
        self.root = root
        self.root.title("NMEA-RTK-PPK Toolkit")
        self.root.geometry("1400x700")
        self.create_widgets()

    def create_widgets(self):
        # Frame for RTCM Parsing and Logging
        rtcm_frame = tk.LabelFrame(
            self.root, text="RTCM 3.3 Parsing and Logging", padx=10, pady=10
        )
        rtcm_frame.pack(fill="x", padx=10, pady=5)

        ## Local RTCM Subsection
        local_rtcm_frame = tk.LabelFrame(
            rtcm_frame, text="Local RTCM Source", padx=10, pady=10
        )
        local_rtcm_frame.pack(fill="x", padx=10, pady=5)

        ### Instruction Label
        instruction_label = tk.Label(
            local_rtcm_frame,
            text="Select either a COM port or enter a TCP/UDP IP address (not both)",
            font=("Arial", 15, "italic"),
            wraplength=800,
            justify="left",
            anchor="w",
        )
        instruction_label.pack(fill="x", padx=5, pady=5)

        ### Dropdown for connected USB ports
        self.local_usb_ports = tk.StringVar(value="Select COM Port")
        self.local_usb_dropdown = ttk.Combobox(
            local_rtcm_frame, textvariable=self.local_usb_ports, state="readonly"
        )
        self.local_usb_dropdown["values"] = self.get_serial_ports()
        self.local_usb_dropdown.pack(side="left", padx=5)

        ### TCP/UDP Entry Field
        self.local_tcp_udp_input = tk.Entry(local_rtcm_frame, width=50)
        self.local_tcp_udp_input.insert(0, "Enter TCP/UDP IP Address")
        self.local_tcp_udp_input.bind(
            "<FocusIn>",
            lambda event: self.clear_placeholder(event, "Enter TCP/UDP IP Address"),
        )
        self.local_tcp_udp_input.pack(side="left", padx=5)

        ### Buttons for Local RTCM
        local_start_btn = tk.Button(
            local_rtcm_frame,
            text="Start Local Stream",
            command=self.start_local_rtcm_logging,
        )
        local_start_btn.pack(side="left", padx=5)

        local_stop_btn = tk.Button(
            local_rtcm_frame,
            text="Stop Local Stream",
            command=self.stop_local_rtcm_logging,
        )
        local_stop_btn.pack(side="left", padx=5)

        refresh_btn = tk.Button(
            local_rtcm_frame, text="Refresh Ports", command=self.refresh_serial_ports
        )
        refresh_btn.pack(side="left", padx=5)

        # Station RTCM Subsection
        station_rtcm_frame = tk.LabelFrame(
            rtcm_frame, text="Station RTCM (NTRIP)", padx=10, pady=10
        )
        station_rtcm_frame.pack(fill="x", padx=10, pady=5)

        # NTRIP Caster Input Field
        self.station_stream_input = tk.Entry(station_rtcm_frame, width=50)
        self.station_stream_input.insert(0, "Enter NTRIP Server/Caster URL or Stream")
        self.station_stream_input.bind(
            "<FocusIn>",
            lambda event: self.clear_placeholder(
                event, "Enter NTRIP Caster URL or Stream"
            ),
        )
        self.station_stream_input.pack(side="left", padx=5)

        # Buttons for Station RTCM
        station_start_btn = tk.Button(
            station_rtcm_frame,
            text="Start Station Stream",
            command=self.start_station_rtcm_logging,
        )
        station_start_btn.pack(side="left", padx=5)

        station_stop_btn = tk.Button(
            station_rtcm_frame,
            text="Stop Station Stream",
            command=self.stop_station_rtcm_logging,
        )
        station_stop_btn.pack(side="left", padx=5)

        # Frame for Consoles
        console_frame = tk.LabelFrame(self.root, text="Console", padx=10, pady=10)
        console_frame.pack(fill="x", padx=10, pady=5)

        # Console Log Subsection - Local
        console_local_frame = tk.LabelFrame(
            console_frame, text="Local Stream", padx=10, pady=10
        )
        console_local_frame.pack(fill="both", padx=5, pady=10)

        self.local_console_log_text = tk.Text(
            console_local_frame, height=10, wrap="none", state="disabled", bg="#f4f4f4"
        )
        self.local_console_log_text.pack(fill="both", padx=5, pady=5)

        # Console Log Subsection - Station
        console_local_frame = tk.LabelFrame(
            console_frame, text="Station Stream", padx=10, pady=10
        )
        console_local_frame.pack(fill="both", padx=5, pady=10)

        self.station_console_log_text = tk.Text(
            console_local_frame, height=10, wrap="none", state="disabled", bg="#f4f4f4"
        )
        self.station_console_log_text.pack(fill="both", padx=5, pady=5)

        # Frame for PPK/RTK File Processing
        file_frame = tk.LabelFrame(self.root, text="File Processing", padx=10, pady=10)
        file_frame.pack(fill="x", padx=10, pady=5)

        load_base_btn = tk.Button(
            file_frame, text="Load Base File", command=self.load_base_file
        )
        load_base_btn.pack(side="left", padx=5)

        load_rover_btn = tk.Button(
            file_frame, text="Load Rover File", command=self.load_rover_file
        )
        load_rover_btn.pack(side="left", padx=5)

        process_btn = tk.Button(
            file_frame, text="Process Data", command=self.process_data
        )
        process_btn.pack(side="left", padx=5)

        # Frame for Report Generation
        report_frame = tk.LabelFrame(
            self.root, text="Report Generation", padx=10, pady=10
        )
        report_frame.pack(fill="x", padx=10, pady=5)

        export_csv_btn = tk.Button(
            report_frame, text="Export to CSV", command=self.export_csv
        )
        export_csv_btn.pack(side="left", padx=5)

        export_pdf_btn = tk.Button(
            report_frame, text="Export to PDF", command=self.export_pdf
        )
        export_pdf_btn.pack(side="left", padx=5)

    # Placeholder Functions for Button Actions
    def start_local_rtcm_logging(self):
        """
        Start Local RTCM Stream Logging.
        Ensures only one input method (COM port or TCP/UDP IP address) is provided.
        """
        com_port = self.local_usb_ports.get()
        tcp_ip = self.local_tcp_udp_input.get().strip()

        if com_port == "Select COM Port" and tcp_ip == "Enter TCP/UDP IP Address":
            messagebox.showerror(
                "Input Error",
                "Please provide either a COM port or a TCP/UDP IP address.",
            )
            return
        if com_port != "Select COM Port" and tcp_ip != "Enter TCP/UDP IP Address":
            messagebox.showerror(
                "Input Error",
                "Please provide only one input: either a COM port or a TCP/UDP IP address.",
            )
            return

        if com_port != "Select COM Port":
            messagebox.showinfo(
                "Info",
                f"Starting Local RTCM Stream Parsing and Logging for {com_port}...",
            )
            # Add functionality to initialize and start the local stream via COM port
        elif tcp_ip != "Enter TCP/UDP IP Address":
            messagebox.showinfo(
                "Info",
                f"Starting Local RTCM Stream Parsing and Logging for {tcp_ip}...",
            )
            # Add functionality to initialize and start the local stream via TCP/UDP

        # Logging callback to update GUI
        def log_to_gui(message):
            # Configure the text tag for red color
            self.local_console_log_text.tag_configure("red", foreground="red")

            # Enable the Text widget, insert the message with the "red" tag, and disable it
            self.local_console_log_text.config(state="normal")
            self.local_console_log_text.insert(
                "end", message, "red"
            )  # Apply the red tag
            self.local_console_log_text.see("end")  # Auto-scroll to the bottom
            self.local_console_log_text.config(state="disabled")

        try:
            if com_port != "Select COM Port":
                self.local_parser = RTCMParser(
                com_port, is_serial=True, baudrate=115200, log_callback=log_to_gui
            )
            else:
                self.local_parser = RTCMParser(
                tcp_ip, is_serial=False, baudrate=115200, log_callback=log_to_gui
                )

            self.local_parser.connect()

            # Start parsing in a separate thread
            thread = threading.Thread(
                target=lambda: self.local_parser.parse_stream(
                    f"./logs/{program_timestamp}_local_rtcm_log.csv"
                ),
                daemon=True,
            )
            thread.start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start local RTCM stream: {e}")

    def stop_local_rtcm_logging(self):
        """
        Stop the Local RTCM Stream Logging.
        """
        if hasattr(self, "local_parser") and self.local_parser is not None:
            self.local_parser.stop()  # Stop the parsing process
            self.local_parser.disconnect()  # Close the connection
            self.local_parser = None  # Clear the parser instance
            messagebox.showinfo("Info", "Local RTCM Stream Logging stopped.")
        else:
            messagebox.showwarning("Warning", "No active Local RTCM stream to stop.")

    @staticmethod
    def start_station_rtcm_logging():
        messagebox.showinfo("Info", "Starting Station RTCM (NTRIP) Stream Logging...")
        # Add functionality to initialize and start the NTRIP station stream

    @staticmethod
    def stop_station_rtcm_logging():
        messagebox.showinfo("Info", "Stopping Station RTCM (NTRIP) Stream Logging...")
        # Add functionality to stop the NTRIP station stream

    @staticmethod
    def load_base_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("GNSS Files", "*.obs;*.rinex"), ("All Files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("Info", f"Base file loaded: {file_path}")

    @staticmethod
    def load_rover_file():
        file_path = filedialog.askopenfilename(
            filetypes=[("GNSS Files", "*.obs;*.rinex"), ("All Files", "*.*")]
        )
        if file_path:
            messagebox.showinfo("Info", f"Rover file loaded: {file_path}")

    @staticmethod
    def process_data():
        messagebox.showinfo("Info", "Processing Data... (Feature in Progress)")

    @staticmethod
    def export_csv():
        messagebox.showinfo("Info", "Exporting to CSV... (Feature in Progress)")

    @staticmethod
    def export_pdf():
        messagebox.showinfo("Info", "Exporting to PDF... (Feature in Progress)")

    @staticmethod
    def clear_placeholder(event, placeholder):
        """
        Clear placeholder text in the Entry widget when it receives focus.
        """
        widget = event.widget
        if widget.get() == placeholder:
            widget.delete(0, tk.END)

    @staticmethod
    def get_serial_ports():
        """
        Get a list of available serial ports.
        """
        return [port.device for port in serial.tools.list_ports.comports()]

    def refresh_serial_ports(self):
        self.local_usb_dropdown["values"] = self.get_serial_ports()
        self.local_usb_ports.set("Select COM Port")


# Main Application Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    try:
        root.state("zoomed")  # Works on Windows and Linux
    except tk.TclError:
        root.geometry(
            f"{root.winfo_screenwidth()}x{root.winfo_screenheight()}+0+0"
        )  # For macOS
    app = PPKRTKToolkit(root)
    root.mainloop()
