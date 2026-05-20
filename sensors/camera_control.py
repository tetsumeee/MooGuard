import os
import time
from datetime import datetime
from picamera2 import Picamera2

class MooGuardCamera:
    def __init__(self):
        """Initializes the Raspberry Pi CSI Camera Module hardware."""
        try:
            self.picam = Picamera2()
            # Configure a standard resolution suitable for report logging
            config = self.picam.create_still_configuration(main={"size": (1280, 720)})
            self.picam.configure(config)
            self.picam.start()
            self.is_ready = True
            print("CSI Camera Module Subsystem: ONLINE")
        except Exception as e:
            print(f"Camera Initialization Error: {e}")
            self.is_ready = False

    def capture_evidence_frame(self, status):
        """Captures a timestamped JPEG image and stores it locally."""
        if not self.is_ready:
            return
            
        try:
            # Create a clean folder structure for the evidence log data
            log_dir = "/home/pi/Desktop/MooGuard/evidence_snapshots"
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
                
            # Create a file name using the exact timestamp format from your project report
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{log_dir}/IMG_{timestamp}_{status}.jpg"
            
            # Write file to storage arrays
            self.picam.capture_file(filename)
            print(f"[AUTONOMOUS CAMERA] 📸 Snapshot stored successfully: {filename}")
        except Exception as e:
            print(f"Failed to capture frame: {e}")

    def close(self):
        if self.is_ready:
            self.picam.stop()