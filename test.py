import cv2
import numpy as np
import yaml

def nothing(x):
    pass

def click_event(event, x, y, flags, param):
    global image, hsv, current_color
    if event == cv2.EVENT_LBUTTONDOWN:
        color = hsv[y, x]
        print(f"Clicked color HSV: {color}")

        # Set trackbar positions for the current color
        cv2.setTrackbarPos('HMin', 'HSV Mask Creator', max(0, color[0] - 10))
        cv2.setTrackbarPos('HMax', 'HSV Mask Creator', min(179, color[0] + 10))
        cv2.setTrackbarPos('SMin', 'HSV Mask Creator', max(0, color[1] - 40))
        cv2.setTrackbarPos('SMax', 'HSV Mask Creator', min(255, color[1] + 40))
        cv2.setTrackbarPos('VMin', 'HSV Mask Creator', max(0, color[2] - 40))
        cv2.setTrackbarPos('VMax', 'HSV Mask Creator', min(255, color[2] + 40))

def update_sliders():
    global current_color, color_ranges
    cv2.setTrackbarPos('HMin', 'HSV Mask Creator', color_ranges[current_color]['HMin'])
    cv2.setTrackbarPos('HMax', 'HSV Mask Creator', color_ranges[current_color]['HMax'])
    cv2.setTrackbarPos('SMin', 'HSV Mask Creator', color_ranges[current_color]['SMin'])
    cv2.setTrackbarPos('SMax', 'HSV Mask Creator', color_ranges[current_color]['SMax'])
    cv2.setTrackbarPos('VMin', 'HSV Mask Creator', color_ranges[current_color]['VMin'])
    cv2.setTrackbarPos('VMax', 'HSV Mask Creator', color_ranges[current_color]['VMax'])

def export_to_yaml():
    global color_ranges
    with open('color_ranges.yaml', 'w') as file:
        yaml.dump(color_ranges, file)
    print("Color ranges exported to color_ranges.yaml")

def button_callback(value):
    global current_color
    if value == "Export":
        export_to_yaml()
    else:
        current_color = value
        update_sliders()
        print(f"Switched to {current_color}")

# Load the image
image = cv2.imread('test.png')
if image is None:
    raise ValueError("Could not read the image. Make sure 'test.png' is in the correct directory.")

# Convert to HSV
hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

# Create windows
cv2.namedWindow('Original Image')
cv2.namedWindow('HSV Mask Creator')

# Set mouse callback for original image window
cv2.setMouseCallback('Original Image', click_event)

# Create trackbars for color change
cv2.createTrackbar('HMin', 'HSV Mask Creator', 0, 179, nothing)
cv2.createTrackbar('HMax', 'HSV Mask Creator', 179, 179, nothing)
cv2.createTrackbar('SMin', 'HSV Mask Creator', 0, 255, nothing)
cv2.createTrackbar('SMax', 'HSV Mask Creator', 255, 255, nothing)
cv2.createTrackbar('VMin', 'HSV Mask Creator', 0, 255, nothing)
cv2.createTrackbar('VMax', 'HSV Mask Creator', 255, 255, nothing)

# Create buttons
cv2.createButton("Color 1", button_callback, "Color 1", cv2.QT_PUSH_BUTTON | cv2.QT_NEW_BUTTONBAR)
cv2.createButton("Color 2", button_callback, "Color 2", cv2.QT_PUSH_BUTTON)
cv2.createButton("Color 3", button_callback, "Color 3", cv2.QT_PUSH_BUTTON)
cv2.createButton("Color 4", button_callback, "Color 4", cv2.QT_PUSH_BUTTON)
cv2.createButton("Export", button_callback, "Export", cv2.QT_PUSH_BUTTON)

# Initialize color ranges
color_ranges = {
    "Color 1": {"HMin": 0, "HMax": 179, "SMin": 0, "SMax": 255, "VMin": 0, "VMax": 255},
    "Color 2": {"HMin": 0, "HMax": 179, "SMin": 0, "SMax": 255, "VMin": 0, "VMax": 255},
    "Color 3": {"HMin": 0, "HMax": 179, "SMin": 0, "SMax": 255, "VMin": 0, "VMax": 255},
    "Color 4": {"HMin": 0, "HMax": 179, "SMin": 0, "SMax": 255, "VMin": 0, "VMax": 255}
}

current_color = "Color 1"

while(1):
    # Get current positions of all trackbars
    hMin = cv2.getTrackbarPos('HMin', 'HSV Mask Creator')
    hMax = cv2.getTrackbarPos('HMax', 'HSV Mask Creator')
    sMin = cv2.getTrackbarPos('SMin', 'HSV Mask Creator')
    sMax = cv2.getTrackbarPos('SMax', 'HSV Mask Creator')
    vMin = cv2.getTrackbarPos('VMin', 'HSV Mask Creator')
    vMax = cv2.getTrackbarPos('VMax', 'HSV Mask Creator')

    # Update color ranges
    color_ranges[current_color] = {
        "HMin": hMin, "HMax": hMax,
        "SMin": sMin, "SMax": sMax,
        "VMin": vMin, "VMax": vMax
    }

    # Set minimum and maximum HSV values to display
    lower = np.array([hMin, sMin, vMin])
    upper = np.array([hMax, sMax, vMax])

    # Create the mask and result
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(image, image, mask=mask)

    # Display result image and original image
    cv2.imshow('HSV Mask Creator', result)
    cv2.imshow('Original Image', image)

    # Wait for 'Esc' key to exit
    k = cv2.waitKey(1) & 0xFF
    if k == 27:
        break

    # Print current values when they change
    current_values = (hMin, sMin, vMin, hMax, sMax, vMax)
    if 'last_values' not in locals() or current_values != last_values:
        print(f"Color: {current_color}, H: {hMin}-{hMax}, S: {sMin}-{sMax}, V: {vMin}-{vMax}")
        last_values = current_values

cv2.destroyAllWindows()
