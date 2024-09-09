# from gpiozero import PWMLED
# from time import sleep
# import math

# # Assign GPIO pin numbers to the red, green, and blue color channels.
# RED_PIN = 17
# GREEN_PIN = 22
# BLUE_PIN = 24

# # Set up the PWM channels for each of the color LEDs (red, green, blue).
# red = PWMLED(RED_PIN)
# green = PWMLED(GREEN_PIN)
# blue = PWMLED(BLUE_PIN)

# # Function to convert a HEX color code into its corresponding RGB values.
# def hex_to_rgb(hex_color):
#     hex_color = hex_color.lstrip('#')  # Remove the '#' character if it exists.
#     # Extract and convert the RGB components from the hex color code.
#     return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# # A function to create a smooth ease-in-out transition effect using a sine wave formula.
# def ease_in_out(t):
#     # The function returns a value that starts slow, speeds up, and then slows down at the end.
#     return 0.5 * (1 - math.cos(math.pi * t))

# Function to smoothly transition the LEDs from black to a specified color and then back to black.
def fade_in_out(hex_color, duration=1, steps=100):
    # # Convert the provided HEX color code into its RGB components.
    # r_target, g_target, b_target = hex_to_rgb(hex_color)
    
    # # Scale the RGB values from the 0-255 range down to the 0-1 range for PWM.
    # r_target, g_target, b_target = r_target / 255.0, g_target / 255.0, b_target / 255.0

    # # The time allocated for each fade (both in and out).
    # fade_time = duration / 1
    # # Calculate the delay between each step of the fade process.
    # delay = fade_time / steps

    # # Begin the fade-in process (transition from black to the specified color).
    # for step in range(steps + 1):
    #     # Calculate the current progress of the fade (from 0 to 1).
    #     t = step / steps
    #     # Apply the ease-in-out function to smooth the transition.
    #     ease_value = ease_in_out(t)
        
    #     # Adjust the intensity of the red, green, and blue channels based on the easing value.
    #     r = r_target * ease_value
    #     g = g_target * ease_value
    #     b = b_target * ease_value

    #     # Set the brightness levels for the red, green, and blue LEDs.
    #     red.value = r
    #     green.value = g
    #     blue.value = b

    #     # Pause briefly before moving to the next step.
    #     sleep(delay)

    # # Start the fade-out process (transition from the specified color back to black).
    # for step in range(steps + 1):
    #     # Calculate the reverse progress of the fade-out (from 1 to 0).
    #     t = step / steps
    #     # Use the ease-in-out function to smooth the fade-out transition.
    #     ease_value = ease_in_out(1 - t)
        
    #     # Adjust the intensity of the red, green, and blue channels based on the reverse easing value.
    #     r = r_target * ease_value
    #     g = g_target * ease_value
    #     b = b_target * ease_value

    #     # Set the brightness levels for the red, green, and blue LEDs accordingly.
    #     red.value = r
    #     green.value = g
    #     blue.value = b
    #     # Pause briefly before moving to the next step.
    #     sleep(delay)
    print("LED SERVICE")
