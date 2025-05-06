#!/usr/bin/env python3
"""
IP Scanner and Scrcpy Launcher (GUI Version)

This script scans the local network for devices with port 5555 open,
allows the user to select one with a GUI, and launches scrcpy to mirror the selected device.
"""

import os
import socket
import subprocess
import ipaddress
import threading
import time
from queue import Queue
import tkinter as tk
from tkinter import ttk, messagebox

class IPScanner:
    def __init__(self):
        self.open_ips = []
        self.ip_queue = Queue()
        self.print_lock = threading.Lock()
        
    def get_network_prefix(self):
        """Get the local network prefix"""
        try:
            # Run hostname command to get local IP
            result = subprocess.run(['hostname', '-I'], capture_output=True, text=True)
            local_ip = result.stdout.strip().split()[0]
            # Extract network prefix (assuming /24 subnet)
            network_prefix = '.'.join(local_ip.split('.')[:3])
            return network_prefix
        except Exception as e:
            print(f"Error getting network prefix: {e}")
            # Fallback to common home network
            return "192.168.1"
    
    def scan_port(self):
        """Scan the port for each IP in the queue"""
        while not self.ip_queue.empty():
            ip = self.ip_queue.get()
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(0.5)
                result = sock.connect_ex((ip, 5555))
                if result == 0:
                    with self.print_lock:
                        self.open_ips.append(ip)
                sock.close()
            except:
                pass
            finally:
                self.ip_queue.task_done()
    
    def scan_network(self):
        """Scan the entire local network for devices with port 5555 open"""
        network_prefix = self.get_network_prefix()
        
        # Put all IPs in the queue
        for i in range(1, 255):
            ip = f"{network_prefix}.{i}"
            self.ip_queue.put(ip)
        
        # Create threads to scan ports
        threads = []
        for _ in range(100):  # Use 100 threads for faster scanning
            t = threading.Thread(target=self.scan_port)
            t.daemon = True
            threads.append(t)
            t.start()
        
        # Wait for all tasks to complete
        self.ip_queue.join()
        
        return self.open_ips

def launch_scrcpy(ip):
    """Launch scrcpy with the selected IP"""
    try:
        print(f"\nLaunching scrcpy to connect to {ip}...")
        cmd = f"scrcpy --tcpip={ip}:5555"
        subprocess.Popen(cmd, shell=True)
        return True
    except Exception as e:
        print(f"Error launching scrcpy: {e}")
        return False

class ScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Android Device Scanner")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Screen state tracking (False = screen is on, True = screen is off)
        self.screen_is_off = False
        
        # Center the window
        self.center_window()
        
        # Check if scrcpy is installed
        self.check_scrcpy()
        
        # Set up the UI
        self.setup_ui()
        
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'+{x}+{y}')
        
    def check_scrcpy(self):
        """Check if scrcpy is installed"""
        try:
            subprocess.run(['which', 'scrcpy'], check=True, stdout=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError:
            messagebox.showerror(
                "Error", 
                "scrcpy is not installed. Please install it first.\n"
                "You can install it using: sudo apt install scrcpy"
            )
            self.root.quit()
            return False
    
    def setup_ui(self):
        """Set up the user interface"""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Android Device Scanner", 
            font=("Helvetica", 16)
        )
        title_label.pack(pady=(0, 10))
        
        # Status label
        self.status_label = ttk.Label(
            main_frame, 
            text="Click 'Scan Network' to find devices with port 5555 open", 
            font=("Helvetica", 10)
        )
        self.status_label.pack(pady=(0, 10))
        
        # Device listbox frame
        list_frame = ttk.LabelFrame(main_frame, text="Available Devices")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Scrollbar for the listbox
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Listbox to show devices
        self.device_listbox = tk.Listbox(
            list_frame,
            font=("Helvetica", 12),
            selectmode=tk.SINGLE,
            height=10,
            yscrollcommand=scrollbar.set
        )
        self.device_listbox.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar.config(command=self.device_listbox.yview)
        
        # Button frame
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=10)
        
        # Scan button
        self.scan_button = ttk.Button(
            button_frame, 
            text="Scan Network", 
            command=self.start_scan
        )
        self.scan_button.pack(side=tk.LEFT, padx=5)
        
        # Connect button
        self.connect_button = ttk.Button(
            button_frame, 
            text="Connect & Mirror", 
            command=self.connect_to_device,
            state=tk.DISABLED
        )
        self.connect_button.pack(side=tk.LEFT, padx=5)
        
        # Screen Off button
        self.screen_off_button = ttk.Button(
            button_frame, 
            text="Screen Off", 
            command=self.screen_off,
            state=tk.NORMAL
        )
        self.screen_off_button.pack(side=tk.LEFT, padx=5)
        
        # Refresh button
        self.refresh_button = ttk.Button(
            button_frame, 
            text="Refresh", 
            command=self.refresh_scan,
            state=tk.DISABLED
        )
        self.refresh_button.pack(side=tk.LEFT, padx=5)
        
        # Exit button
        exit_button = ttk.Button(
            button_frame, 
            text="Exit", 
            command=self.root.destroy
        )
        exit_button.pack(side=tk.RIGHT, padx=5)
        
        # Double-click binding for list items
        self.device_listbox.bind('<Double-1>', lambda e: self.connect_to_device())
        
    def start_scan(self):
        """Start scanning the network"""
        self.status_label.config(text="Scanning network for devices with port 5555 open...")
        self.scan_button.config(state=tk.DISABLED)
        self.device_listbox.delete(0, tk.END)
        
        # Create and start scanning thread
        scan_thread = threading.Thread(target=self.scan_thread)
        scan_thread.daemon = True
        scan_thread.start()
    
    def refresh_scan(self):
        """Refresh the scan results"""
        self.start_scan()
    
    def scan_thread(self):
        """Background thread for scanning"""
        scanner = IPScanner()
        self.devices = scanner.scan_network()
        
        # Update UI from main thread
        self.root.after(0, self.update_device_list)
        
    def update_device_list(self):
        """Update the device list in the UI"""
        self.device_listbox.delete(0, tk.END)
        
        if not self.devices:
            self.status_label.config(text="No devices found. Make sure devices are on the same network with port 5555 open.")
            self.connect_button.config(state=tk.DISABLED)
            messagebox.showinfo(
                "No Devices Found", 
                "No devices with port 5555 open found on the network.\n\n"
                "Make sure your Android device:\n"
                "1. Is connected to the same network\n"
                "2. Has USB debugging enabled\n"
                "3. Has ADB over TCP/IP enabled (run 'adb tcpip 5555' when connected via USB)"
            )
        else:
            self.status_label.config(text=f"Found {len(self.devices)} device(s) with port 5555 open")
            for ip in self.devices:
                self.device_listbox.insert(tk.END, ip)
            self.connect_button.config(state=tk.NORMAL)
            
        self.scan_button.config(state=tk.NORMAL)
        self.refresh_button.config(state=tk.NORMAL)
        
    def connect_to_device(self):
        """Connect to the selected device"""
        selected_index = self.device_listbox.curselection()
        if not selected_index:
            messagebox.showinfo("Selection Required", "Please select a device first.")
            return
            
        selected_ip = self.devices[selected_index[0]]
        self.status_label.config(text=f"Connecting to {selected_ip}...")
        
        # Launch scrcpy in a separate thread to avoid freezing UI
        thread = threading.Thread(target=lambda: launch_scrcpy(selected_ip))
        thread.daemon = True
        thread.start()
        
    def screen_off(self):
        """Toggle the device screen on/off by sending the appropriate keyboard shortcut to the scrcpy window"""
        try:
            # Try to find all scrcpy windows using a pattern match instead of exact name
            find_cmd = subprocess.run(
                ['xdotool', 'search', '--class', 'scrcpy'], 
                capture_output=True, 
                text=True
            )
            
            if not find_cmd.stdout.strip():
                # Try alternative search if the class approach didn't work
                find_cmd = subprocess.run(
                    ['xdotool', 'search', '--name', 'scrcpy'], 
                    capture_output=True, 
                    text=True
                )
            
            if find_cmd.stdout.strip():
                # Get the window IDs
                window_ids = find_cmd.stdout.strip().split('\n')
                # Use the latest window (usually the last in the list)
                window_id = window_ids[-1]
                
                # Determine which command to send based on screen state
                if not self.screen_is_off:
                    # Screen is currently ON, turn it OFF with Alt+O
                    key_command = 'alt+o'
                    status_message = "Turning screen OFF..."
                    result_message = "Screen turned OFF"
                else:
                    # Screen is currently OFF, turn it ON with Alt+Shift+O
                    key_command = 'alt+shift+o'
                    status_message = "Turning screen ON..."
                    result_message = "Screen turned ON"
                
                # Display a message to inform the user
                self.status_label.config(text=f"Focusing scrcpy window and {status_message}")
                
                # Update the UI to show immediate feedback
                self.root.update_idletasks()
                
                # Give the GUI time to update
                time.sleep(0.1)
                
                # Focus on the scrcpy window (use windowactivate for reliable focusing)
                subprocess.run(['xdotool', 'windowactivate', '--sync', window_id])
                
                # Wait for window to be active
                time.sleep(0.3)
                
                # Send keyboard shortcut using xdotool
                subprocess.run(['xdotool', 'key', key_command])
                
                # Toggle the screen state
                self.screen_is_off = not self.screen_is_off
                
                # Update button text and status label
                self.screen_off_button.config(text="Screen On" if self.screen_is_off else "Screen Off")
                self.status_label.config(text=result_message)
            else:
                # Try one more approach - search for any window containing "scrcpy" in the name
                find_cmd = subprocess.run(
                    ['xdotool', 'search', '--onlyvisible', '--name', '.*scrcpy.*'], 
                    capture_output=True, 
                    text=True
                )
                
                if find_cmd.stdout.strip():
                    window_ids = find_cmd.stdout.strip().split('\n')
                    window_id = window_ids[-1]
                    
                    # Determine which command to send based on screen state
                    if not self.screen_is_off:
                        # Screen is currently ON, turn it OFF with Alt+O
                        key_command = 'alt+o'
                        status_message = "Turning screen OFF..."
                        result_message = "Screen turned OFF"
                    else:
                        # Screen is currently OFF, turn it ON with Alt+Shift+O
                        key_command = 'alt+shift+o'
                        status_message = "Turning screen ON..."
                        result_message = "Screen turned ON"
                    
                    self.status_label.config(text=f"Focusing scrcpy window (pattern match) and {status_message}")
                    self.root.update_idletasks()
                    time.sleep(0.1)
                    
                    subprocess.run(['xdotool', 'windowactivate', '--sync', window_id])
                    time.sleep(0.3)
                    subprocess.run(['xdotool', 'key', key_command])
                    
                    # Toggle the screen state
                    self.screen_is_off = not self.screen_is_off
                    
                    # Update button text and status label
                    self.screen_off_button.config(text="Screen On" if self.screen_is_off else "Screen Off")
                    self.status_label.config(text=result_message)
                else:
                    self.status_label.config(text="No scrcpy window found. Launch scrcpy first.")
                    messagebox.showinfo("No Window Found", "No scrcpy window found. Please connect to a device first.")
        except Exception as e:
            self.status_label.config(text=f"Error sending screen command: {e}")
            print(f"Error sending screen command: {e}")

def main():
    root = tk.Tk()
    app = ScannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()