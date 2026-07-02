"""
Screen Capture Module for AI Study Partner
Handles real-time screen capture and frame processing
"""

import mss
import cv2
import numpy as np
import time
import threading
from typing import Optional, Callable, Tuple
from dataclasses import dataclass
import os
from PIL import Image
import io
import base64
import ctypes
from ctypes import wintypes

@dataclass
class CaptureConfig:
    """Configuration for screen capture"""
    fps: int = 1
    region: Optional[Tuple[int, int, int, int]] = None  # (x, y, width, height)
    quality: int = 80
    format: str = "JPEG"
    # 1-based monitor index as used by mss.monitors (1 is primary)
    monitor_index: int = 1

class ScreenCapture:
    """Real-time screen capture with configurable regions and FPS"""
    
    def __init__(self, config: Optional[CaptureConfig] = None):
        self.config = config or CaptureConfig()
        self.sct = None  # Will be created in each thread
        self.is_capturing = False
        self.capture_thread: Optional[threading.Thread] = None
        self.frame_callback: Optional[Callable] = None
        self.last_frame: Optional[np.ndarray] = None
        self.frame_count = 0
        self.start_time = None
        
    def set_callback(self, callback: Callable[[np.ndarray, float], None]):
        """Set callback function for new frames"""
        self.frame_callback = callback
        
    def start_capture(self, region: Optional[Tuple[int, int, int, int]] = None):
        """Start continuous screen capture"""
        if self.is_capturing:
            return
            
        self.is_capturing = True
        self.start_time = time.time()
        self.frame_count = 0
        
        # Use provided region or default to full screen
        if region:
            self.config.region = region
        elif self.config.region is None:
            # Default to full screen - get monitor info from a temporary MSS instance
            with mss.mss() as temp_sct:
                idx = self.config.monitor_index if 0 < self.config.monitor_index < len(temp_sct.monitors) else 1
                monitor = temp_sct.monitors[idx]
                self.config.region = (monitor["left"], monitor["top"], 
                                    monitor["width"], monitor["height"])
        
        self.capture_thread = threading.Thread(target=self._capture_loop)
        self.capture_thread.daemon = True
        self.capture_thread.start()
        
    def stop_capture(self):
        """Stop screen capture"""
        self.is_capturing = False
        if self.capture_thread:
            self.capture_thread.join(timeout=2.0)
            
    def capture_single_frame(self, region: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """Capture a single frame"""
        # Create MSS instance for this thread
        with mss.mss() as sct:
            if region:
                monitor = {
                    "top": region[1],
                    "left": region[0], 
                    "width": region[2],
                    "height": region[3]
                }
            else:
                idx = self.config.monitor_index if 0 < self.config.monitor_index < len(sct.monitors) else 1
                monitor = sct.monitors[idx]
                
            screenshot = sct.grab(monitor)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            
            # Convert PIL to OpenCV format
            frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            return frame
        
    def _capture_loop(self):
        """Main capture loop running in separate thread"""
        frame_interval = 1.0 / self.config.fps
        
        # Create MSS instance for this thread
        with mss.mss() as sct:
            while self.is_capturing:
                start_frame_time = time.time()
                
                try:
                    # Capture frame using thread-local MSS instance
                    if self.config.region:
                        monitor = {
                            "top": self.config.region[1],
                            "left": self.config.region[0], 
                            "width": self.config.region[2],
                            "height": self.config.region[3]
                        }
                    else:
                        idx = self.config.monitor_index if 0 < self.config.monitor_index < len(sct.monitors) else 1
                        monitor = sct.monitors[idx]
                        
                    screenshot = sct.grab(monitor)
                    img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
                    
                    # Convert PIL to OpenCV format
                    frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    self.last_frame = frame
                    self.frame_count += 1
                    
                    # Calculate timestamp
                    timestamp = time.time() - self.start_time if self.start_time else 0
                    
                    # Call callback if set
                    if self.frame_callback:
                        self.frame_callback(frame, timestamp)
                        
                except Exception as e:
                    print(f"Error capturing frame: {e}")
                    
                # Maintain FPS
                elapsed = time.time() - start_frame_time
                sleep_time = max(0, frame_interval - elapsed)
                if sleep_time > 0:
                    time.sleep(sleep_time)
                
    def get_frame_as_base64(self, frame: Optional[np.ndarray] = None) -> str:
        """Convert frame to base64 string for API responses"""
        if frame is None:
            frame = self.last_frame
            
        if frame is None or not hasattr(frame, 'shape'):
            return ""
            
        # Encode frame as JPEG
        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, self.config.quality])
        img_base64 = base64.b64encode(buffer).decode('utf-8')
        return img_base64
        
    def get_capture_stats(self) -> dict:
        """Get capture statistics"""
        if not self.start_time:
            return {"status": "not_started"}
            
        elapsed = time.time() - self.start_time
        actual_fps = self.frame_count / elapsed if elapsed > 0 else 0
        
        return {
            "status": "capturing" if self.is_capturing else "stopped",
            "frame_count": self.frame_count,
            "elapsed_time": elapsed,
            "target_fps": self.config.fps,
            "actual_fps": actual_fps,
            "region": self.config.region
        }
        
    def cleanup(self):
        """Cleanup resources"""
        self.stop_capture()
        # No persistent MSS handle to close
        return

    @staticmethod
    def list_monitors() -> list:
        """Return a list of available monitors with geometry info"""
        monitors = []
        with mss.mss() as sct:
            for idx, mon in enumerate(sct.monitors):
                # mss.monitors[0] is a virtual bbox of all monitors; skip it
                if idx == 0:
                    continue
                monitors.append({
                    "index": idx,
                    "left": mon.get("left", 0),
                    "top": mon.get("top", 0),
                    "width": mon.get("width", 0),
                    "height": mon.get("height", 0)
                })
        return monitors

    @staticmethod
    def capture_monitor_thumbnail(index: int, quality: int = 60, max_width: int = 640) -> str:
        """Capture a single frame for the given monitor index and return base64 JPEG thumbnail"""
        with mss.mss() as sct:
            if not (0 < index < len(sct.monitors)):
                index = 1
            mon = sct.monitors[index]
            screenshot = sct.grab(mon)
            img = Image.frombytes("RGB", screenshot.size, screenshot.bgra, "raw", "BGRX")
            # Downscale if wider than max_width
            if img.width > max_width:
                ratio = max_width / float(img.width)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.LANCZOS)
            buf = io.BytesIO()
            img.save(buf, format="JPEG", quality=quality)
            return base64.b64encode(buf.getvalue()).decode("utf-8")

    # -------------------- Windows enumeration (Windows only) --------------------
    @staticmethod
    def list_windows() -> list:
        """Enumerate top-level visible windows with titles and rectangles (Windows only)."""
        windows: list = []
        user32 = ctypes.windll.user32

        WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
        IsWindowVisible = user32.IsWindowVisible
        GetWindowTextW = user32.GetWindowTextW
        GetWindowTextLengthW = user32.GetWindowTextLengthW
        GetWindowRect = user32.GetWindowRect

        rect = wintypes.RECT()

        def _callback(hwnd, lParam):
            try:
                if IsWindowVisible(hwnd):
                    length = GetWindowTextLengthW(hwnd)
                    if length > 0:
                        buffer = ctypes.create_unicode_buffer(length + 1)
                        GetWindowTextW(hwnd, buffer, length + 1)
                        title = buffer.value.strip()
                        if title:
                            if GetWindowRect(hwnd, ctypes.byref(rect)):
                                left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
                                width = max(0, right - left)
                                height = max(0, bottom - top)
                                # Filter out very small windows
                                if width >= 100 and height >= 80:
                                    windows.append({
                                        "hwnd": int(hwnd),
                                        "title": title,
                                        "left": left,
                                        "top": top,
                                        "width": width,
                                        "height": height
                                    })
            except Exception:
                pass
            return True

        user32.EnumWindows(WNDENUMPROC(_callback), 0)
        return windows

    @staticmethod
    def capture_window_thumbnail(hwnd: int, quality: int = 60, max_width: int = 640) -> str:
        """Capture a thumbnail image for a specific window by its handle (Windows only), using PrintWindow to avoid occlusion."""
        user32 = ctypes.windll.user32
        gdi32 = ctypes.windll.gdi32
        rect = wintypes.RECT()
        if not user32.GetWindowRect(ctypes.wintypes.HWND(hwnd), ctypes.byref(rect)):
            return ""
        left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
        width, height = max(0, right - left), max(0, bottom - top)
        if width == 0 or height == 0:
            return ""

        hdc_window = user32.GetWindowDC(ctypes.wintypes.HWND(hwnd))
        if not hdc_window:
            return ""
        hdc_mem = gdi32.CreateCompatibleDC(hdc_window)
        hbmp = gdi32.CreateCompatibleBitmap(hdc_window, width, height)
        if not hbmp:
            gdi32.DeleteDC(hdc_mem)
            user32.ReleaseDC(ctypes.wintypes.HWND(hwnd), hdc_window)
            return ""
        gdi32.SelectObject(hdc_mem, hbmp)

        # 0x00000002 = PW_RENDERFULLCONTENT (Windows 8+)
        user32.PrintWindow(ctypes.wintypes.HWND(hwnd), hdc_mem, 0x00000002)

        # Prepare BITMAPINFO structure
        class BITMAPINFOHEADER(ctypes.Structure):
            _fields_ = [
                ("biSize", wintypes.DWORD),
                ("biWidth", ctypes.c_long),
                ("biHeight", ctypes.c_long),
                ("biPlanes", wintypes.WORD),
                ("biBitCount", wintypes.WORD),
                ("biCompression", wintypes.DWORD),
                ("biSizeImage", wintypes.DWORD),
                ("biXPelsPerMeter", ctypes.c_long),
                ("biYPelsPerMeter", ctypes.c_long),
                ("biClrUsed", wintypes.DWORD),
                ("biClrImportant", wintypes.DWORD),
            ]
        class BITMAPINFO(ctypes.Structure):
            _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]

        bmi = BITMAPINFO()
        bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
        bmi.bmiHeader.biWidth = width
        bmi.bmiHeader.biHeight = -height  # top-down
        bmi.bmiHeader.biPlanes = 1
        bmi.bmiHeader.biBitCount = 32
        bmi.bmiHeader.biCompression = 0  # BI_RGB

        buf_len = width * height * 4
        pixel_buf = (ctypes.c_byte * buf_len)()
        gdi32.GetDIBits(hdc_mem, hbmp, 0, height, ctypes.byref(pixel_buf), ctypes.byref(bmi), 0)

        # Clean up GDI objects
        gdi32.DeleteObject(hbmp)
        gdi32.DeleteDC(hdc_mem)
        user32.ReleaseDC(ctypes.wintypes.HWND(hwnd), hdc_window)

        # Create image from BGRA buffer
        img = Image.frombuffer("RGBA", (width, height), pixel_buf, "raw", "BGRA", 0, 1).convert("RGB")
        if img.width > max_width:
            ratio = max_width / float(img.width)
            img = img.resize((int(img.width * ratio), int(img.height * ratio)), Image.LANCZOS)
        buf = io.BytesIO()
        img.save(buf, format="JPEG", quality=quality)
        return base64.b64encode(buf.getvalue()).decode("utf-8")
