#!/usr/bin/env python3
"""
Pi Day Circle Drawing Automation

Automates drawing a perfect circle in the Pi Day Challenge game
(https://yage.ai/genai/pi.html) using GUI automation.

This script:
1. Opens a browser and navigates to the game
2. Detects the canvas element position
3. Calculates perfect circle coordinates
4. Uses PyAutoGUI to draw the circle with precise mouse movements
"""

import time
import math
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


# Configure PyAutoGUI
pyautogui.PAUSE = 0.01  # Small pause between actions for smooth movement
pyautogui.FAILSAFE = True  # Move mouse to corner to abort


def setup_browser():
    """
    Set up Chrome WebDriver and navigate to the Pi Day Challenge game.

    Returns:
        WebDriver instance
    """
    chrome_options = Options()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')

    try:
        driver = webdriver.Chrome(options=chrome_options)
        print("Opening Pi Day Challenge game...")
        driver.get("https://yage.ai/genai/pi.html")

        # Maximize window to ensure consistent positioning
        print("Maximizing browser window for consistent coordinates...")
        driver.maximize_window()

        # Wait for page to load
        print("Waiting for game to load...")
        time.sleep(3)

        return driver
    except Exception as e:
        print(f"Error setting up Chrome driver: {e}")
        print("\nMake sure you have:")
        print("1. Chrome browser installed")
        print("2. ChromeDriver installed (brew install chromedriver on macOS)")
        raise


def detect_canvas(driver):
    """
    Detect the canvas element and return it along with its properties.

    Args:
        driver: Selenium WebDriver instance

    Returns:
        tuple: (canvas_element, center_x, center_y, radius) where coordinates are relative to canvas
    """
    try:
        # Try to find canvas element - it might be in different locations
        # Common selectors for canvas elements
        canvas_selectors = [
            "canvas",
            "#canvas",
            ".canvas",
            "[id*='canvas']",
            "[class*='canvas']"
        ]

        canvas = None
        for selector in canvas_selectors:
            try:
                if selector.startswith("#"):
                    canvas = driver.find_element(By.ID, selector[1:])
                elif selector.startswith("."):
                    canvas = driver.find_element(By.CLASS_NAME, selector[1:])
                elif selector.startswith("["):
                    # Try by CSS selector
                    canvas = driver.find_element(By.CSS_SELECTOR, selector)
                else:
                    canvas = driver.find_element(By.TAG_NAME, selector)

                if canvas:
                    break
            except NoSuchElementException:
                continue

        if not canvas:
            # Try to find any canvas element
            canvas = driver.find_element(By.TAG_NAME, "canvas")

        # Get canvas size
        size = canvas.size

        print(f"Canvas found! Size: {size}")

        # Calculate center point relative to canvas top-left (0,0 is top-left)
        # ActionChains.move_to_element_with_offset uses offsets from top-left corner
        canvas_center_x = size['width'] / 2
        canvas_center_y = size['height'] / 2

        # Calculate maximum radius (use 40% of the smaller dimension to ensure it fits)
        max_radius = min(size['width'], size['height']) * 0.4

        print(f"Canvas center (offset from top-left): ({canvas_center_x}, {canvas_center_y})")
        print(f"Maximum radius: {max_radius}")

        return canvas, canvas_center_x, canvas_center_y, max_radius

    except NoSuchElementException:
        print("Error: Could not find canvas element")
        raise

    except Exception as e:
        print(f"Error detecting canvas: {e}")
        raise


def calculate_circle_points(radius, num_points=360):
    """
    Calculate points along a perfect circle circumference relative to center (0,0).

    Args:
        radius: Radius of the circle
        num_points: Number of points to generate (default: 360 for 1 degree increments)

    Returns:
        list: List of (offset_x, offset_y) tuples representing points relative to center
    """
    points = []

    for i in range(num_points + 1):  # +1 to close the circle
        # Calculate angle in radians
        angle = 2 * math.pi * i / num_points

        # Calculate point coordinates using parametric circle equation
        # These are offsets from the center (0,0)
        offset_x = radius * math.cos(angle)
        offset_y = radius * math.sin(angle)

        points.append((offset_x, offset_y))

    return points


def draw_circle(driver, canvas, center_x, center_y, points, delay=0.01):
    """
    Use JavaScript to simulate mouse events and draw on the canvas.

    Args:
        driver: Selenium WebDriver instance
        canvas: Canvas WebElement
        center_x: X coordinate of circle center relative to canvas
        center_y: Y coordinate of circle center relative to canvas
        points: List of (offset_x, offset_y) tuples relative to center
        delay: Delay between mouse movements in seconds (default: 0.01)
    """
    if not points:
        print("Error: No points to draw")
        return

    print(f"Drawing circle with {len(points)} points using JavaScript mouse events...")
    print("This method simulates real mouse events on the canvas!")

    print("Starting in 2 seconds...")
    time.sleep(2)

    try:
        # Scroll canvas into view
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});", canvas)
        time.sleep(0.2)

        # Get the starting point
        start_offset_x, start_offset_y = points[0]
        start_x = center_x + start_offset_x
        start_y = center_y + start_offset_y

        # JavaScript to trigger mouse events
        trigger_mousedown = """
        var canvas = arguments[0];
        var x = arguments[1];
        var y = arguments[2];
        var rect = canvas.getBoundingClientRect();
        var event = new MouseEvent('mousedown', {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: rect.left + x,
            clientY: rect.top + y,
            button: 0
        });
        canvas.dispatchEvent(event);
        """

        trigger_mousemove = """
        var canvas = arguments[0];
        var x = arguments[1];
        var y = arguments[2];
        var rect = canvas.getBoundingClientRect();
        var event = new MouseEvent('mousemove', {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: rect.left + x,
            clientY: rect.top + y,
            button: 0,
            buttons: 1
        });
        canvas.dispatchEvent(event);
        """

        trigger_mouseup = """
        var canvas = arguments[0];
        var x = arguments[1];
        var y = arguments[2];
        var rect = canvas.getBoundingClientRect();
        var event = new MouseEvent('mouseup', {
            view: window,
            bubbles: true,
            cancelable: true,
            clientX: rect.left + x,
            clientY: rect.top + y,
            button: 0
        });
        canvas.dispatchEvent(event);
        """

        # Start drawing: mousedown at starting point
        print("Starting to draw...")
        driver.execute_script(trigger_mousedown, canvas, start_x, start_y)
        time.sleep(0.05)

        # Draw through all points
        for i, (offset_x, offset_y) in enumerate(points[1:], 1):
            x = center_x + offset_x
            y = center_y + offset_y

            # Trigger mousemove event
            driver.execute_script(trigger_mousemove, canvas, x, y)
            time.sleep(delay)

            if i % 50 == 0:  # Progress indicator
                print(f"  Progress: {i}/{len(points)-1} points")

        # End drawing: mouseup at last point
        last_offset_x, last_offset_y = points[-1]
        last_x = center_x + last_offset_x
        last_y = center_y + last_offset_y
        driver.execute_script(trigger_mouseup, canvas, last_x, last_y)
        time.sleep(0.1)

        print("Circle drawing complete!")

    except Exception as e:
        print(f"Error during drawing: {e}")
        import traceback
        traceback.print_exc()


def draw_circle_pyautogui(driver, canvas, center_x, center_y, points, delay=0.01):
    """
    Fallback method: Use PyAutoGUI to draw on the canvas by calculating absolute screen coordinates.

    Args:
        driver: Selenium WebDriver instance
        canvas: Canvas WebElement
        center_x: X coordinate of circle center relative to canvas
        center_y: Y coordinate of circle center relative to canvas
        points: List of (offset_x, offset_y) tuples relative to center
        delay: Delay between mouse movements in seconds (default: 0.01)
    """
    if not points:
        print("Error: No points to draw")
        return

    print(f"Drawing circle with {len(points)} points using PyAutoGUI...")

    try:
        # Get canvas absolute position on screen
        canvas_location = canvas.location
        canvas_size = canvas.size

        # Get window position
        window_pos_script = """
        return {
            x: window.screenX || window.screenLeft || 0,
            y: window.screenY || window.screenTop || 0
        };
        """
        try:
            window_pos = driver.execute_script(window_pos_script)
            window_x = window_pos.get('x', 0) if isinstance(window_pos, dict) else 0
            window_y = window_pos.get('y', 0) if isinstance(window_pos, dict) else 0
        except:
            window_x = 0
            window_y = 0

        # Calculate absolute screen coordinates for canvas top-left
        canvas_screen_x = canvas_location['x'] + window_x
        canvas_screen_y = canvas_location['y'] + window_y

        # If coordinates are negative, use viewport coordinates (window must be focused)
        if canvas_screen_x < 0 or canvas_screen_y < 0:
            print("Using viewport coordinates (ensure browser window is focused)...")
            canvas_screen_x = canvas_location['x']
            canvas_screen_y = canvas_location['y']

        print(f"Canvas screen position: ({canvas_screen_x}, {canvas_screen_y})")
        print("Starting in 2 seconds... Make sure browser window is focused!")
        time.sleep(2)

        # Get starting point in screen coordinates
        start_offset_x, start_offset_y = points[0]
        start_screen_x = canvas_screen_x + center_x + start_offset_x
        start_screen_y = canvas_screen_y + center_y + start_offset_y

        print(f"Starting point (screen): ({start_screen_x}, {start_screen_y})")

        # Move to starting point
        pyautogui.moveTo(start_screen_x, start_screen_y, duration=0.1)
        time.sleep(0.1)

        # Press and hold mouse button
        pyautogui.mouseDown()

        # Draw through all points
        for i, (offset_x, offset_y) in enumerate(points[1:], 1):
            x = canvas_screen_x + center_x + offset_x
            y = canvas_screen_y + center_y + offset_y

            pyautogui.moveTo(x, y, duration=delay)

            if i % 50 == 0:
                print(f"  Progress: {i}/{len(points)-1} points")

        # Release mouse button
        pyautogui.mouseUp()

        print("Circle drawing complete!")

    except Exception as e:
        print(f"Error during PyAutoGUI drawing: {e}")
        import traceback
        traceback.print_exc()
        # Make sure to release mouse button
        try:
            pyautogui.mouseUp()
        except:
            pass


def main():
    """
    Main execution flow for the Pi Day circle automation.
    """
    driver = None

    try:
        # Step 1: Setup browser and navigate to game
        driver = setup_browser()

        # Ensure browser window is focused/active
        print("Ensuring browser window is focused...")
        driver.switch_to.window(driver.current_window_handle)
        time.sleep(0.5)

        # Step 2: Detect canvas element
        canvas, center_x, center_y, radius = detect_canvas(driver)

        # Step 3: Calculate circle points (relative to center)
        print(f"\nCalculating circle points...")
        points = calculate_circle_points(radius, num_points=360)
        print(f"Generated {len(points)} points for the circle")

        # Step 4: Brief pause for user to see setup
        print("\n" + "="*50)
        print("Ready to draw!")
        print("="*50)
        print("The script will now draw a perfect circle.")
        print("Keep the browser window visible and active.")
        print("\nTip: For best results, don't move the mouse during drawing.")

        # Step 5: Draw the circle
        # Try JavaScript method first, fallback to PyAutoGUI if needed
        try:
            draw_circle(driver, canvas, center_x, center_y, points, delay=0.01)
        except Exception as e:
            print(f"\nJavaScript method failed: {e}")
            print("Trying PyAutoGUI method as fallback...")
            draw_circle_pyautogui(driver, canvas, center_x, center_y, points, delay=0.01)

        # Step 6: Keep browser open to view results
        print("\nKeeping browser open for 10 seconds to view results...")
        print("Check your ranking in the game!")
        time.sleep(10)

        # Optional: Keep browser open longer
        response = input("\nPress Enter to close the browser, or type 'keep' to keep it open: ")
        if response.lower() != 'keep':
            print("Closing browser...")
            driver.quit()
        else:
            print("Browser will remain open. Close it manually when done.")

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        if driver:
            driver.quit()
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        if driver:
            driver.quit()


if __name__ == "__main__":
    main()
