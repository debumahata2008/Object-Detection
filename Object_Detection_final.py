import cv2
import time
import math


# SETTINGS


# Approximate camera focal length in pixels.

FOCAL_LENGTH = 700

# Approximate real width of the detected object in meters.

REAL_OBJECT_WIDTH = 1.8


# CALCULATE DISTANCE


def calculate_distance(pixel_width):
    if pixel_width <= 0:
        return 0

    distance = (REAL_OBJECT_WIDTH * FOCAL_LENGTH) / pixel_width
    return distance



# CAMERA


camera = cv2.VideoCapture(0)

previous_distance = None
previous_time = None

while True:

    ret, frame = camera.read()

    if not ret:
        print("Camera error!")
        break

    
    # TEMPORARY OBJECT DETECTION
    
   

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Threshold
    _, threshold = cv2.threshold(
        gray, 100, 255, cv2.THRESH_BINARY
    )

    contours, _ = cv2.findContours(
        threshold,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    largest_object = None
    largest_area = 0

    for contour in contours:

        x, y, w, h = cv2.boundingRect(contour)

        area = w * h

        if area > largest_area and w > 50 and h > 50:

            largest_area = area
            largest_object = (x, y, w, h)

    
    # DISTANCE + SPEED
    
    if largest_object:

        x, y, w, h = largest_object

        # Draw object
        cv2.rectangle(
            frame,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        # Calculate distance
        distance = calculate_distance(w)

        # Current time
        current_time = time.time()

        speed = 0

        if previous_distance is not None:

            time_difference = current_time - previous_time

            if time_difference > 0:

                # Distance change in meters
                distance_change = previous_distance - distance

                # Relative speed in m/s
                speed = distance_change / time_difference

                # Convert m/s to km/h
                speed_kmh = speed * 3.6

            else:
                speed_kmh = 0

        else:
            speed_kmh = 0

        previous_distance = distance
        previous_time = current_time

       
        # DISPLAY INFORMATION
        
        cv2.putText(
            frame,
            f"Distance: {distance:.2f} m",
            (20, 40),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"Relative Speed: {speed_kmh:.2f} km/h",
            (20, 75),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 255),
            2
        )

        
        # SAFETY WARNING
        

        if distance < 5:

            cv2.putText(
                frame,
                "!!! DANGER !!!",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.2,
                (0, 0, 255),
                3
            )

        elif distance < 10:

            cv2.putText(
                frame,
                "WARNING: OBJECT NEAR",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 165, 255),
                2
            )

        else:

            cv2.putText(
                frame,
                "SAFE DISTANCE",
                (20, 120),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 255, 0),
                2
            )

    # Show camera
    cv2.imshow("Smart Vehicle Detection", frame)

    # Press Q to exit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break


camera.release()
cv2.destroyAllWindows()