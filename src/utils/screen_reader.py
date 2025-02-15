import pyautogui
import pytesseract
from PIL import Image
import numpy as np
import cv2
import win32gui
import win32con
import win32ui
from typing import Tuple, Optional


class ScreenReader:
    @staticmethod
    def get_window_rect(window_title: str) -> Optional[Tuple[int, int, int, int]]:
        """Get coordinates of a window by title"""
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            if hwnd:
                rect = win32gui.GetWindowRect(hwnd)
                return rect
            return None
        except Exception as e:
            print(f"Error getting window: {e}")
            return None

    @staticmethod
    def capture_window(window_title: str) -> Optional[Image.Image]:
        """Capture specific window content"""
        try:
            # Get window handle
            hwnd = win32gui.FindWindow(None, window_title)
            if not hwnd:
                return None

            # Get window size
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            width = right - left
            height = bottom - top

            # Get window DC
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # Copy window content
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)

            # Convert to PIL Image
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)

            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            return im
        except Exception as e:
            print(f"Error capturing window: {e}")
            return None

    @staticmethod
    def read_text_from_image(image: Image.Image, is_code: bool = False) -> str:
        """Extract text from image"""
        try:
            # Convert to numpy array
            img_np = np.array(image)

            # Convert to grayscale
            gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)

            # Apply thresholding for better text detection
            _, threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Use different OCR configs for code vs regular text
            if is_code:
                custom_config = r'--oem 3 --psm 6 -c preserve_interword_spaces=1'
            else:
                custom_config = r'--oem 3 --psm 6'

            # Perform OCR
            text = pytesseract.image_to_string(threshold, config=custom_config)
            return text.strip()
        except Exception as e:
            print(f"Error reading text: {e}")
            return ""

    @staticmethod
    def read_code_from_editor() -> str:
        """Read code from active editor window"""
        try:
            # Common editor titles
            editor_titles = [
                "Visual Studio Code",
                "- Visual Studio Code",
                "VSCodium",
                "Sublime Text",
                "PyCharm",
                "IntelliJ IDEA"
            ]

            # Try to find and capture editor window
            for title in editor_titles:
                # Find windows that contain the title
                def callback(hwnd, windows):
                    if win32gui.IsWindowVisible(hwnd):
                        window_text = win32gui.GetWindowText(hwnd)
                        if title in window_text:
                            windows.append((hwnd, window_text))
                    return True

                windows = []
                win32gui.EnumWindows(callback, windows)

                if windows:
                    # Use the first matching window
                    hwnd, full_title = windows[0]
                    image = ScreenReader.capture_window(full_title)
                    if image:
                        return ScreenReader.read_text_from_image(image, is_code=True)

            return ""
        except Exception as e:
            print(f"Error reading code: {e}")
            return ""