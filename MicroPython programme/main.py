# ----- Library imports -----#

from ili934xnew import ILI9341, color565
from machine import Pin, SPI
from micropython import const
import tt14
import time

import network
from umqtt.robust import MQTTClient
import json

# ----- Initialization of needed values -----#

# Defining the button pin used for moving forvard through list of channels
button0 = Pin(0)
button1 = Pin(1)
button2 = Pin(2)
button3 = Pin(3)

# Defining Channel class


class Channel:
    # Constructor with all parameters
    def __init__(self, name, views, subs):
        self.name = name
        self.views = views
        self.subs = subs

    # print method that prints each attribute (can be used for debug)
    def print_values(self):
        print("name:", self.name)
        print("views:", self.views)
        print("subs:", self.subs)


# Defining a list to store active channel objects
channel_list = []

# Defining the current channel index, -1 if channel_list is empty
current_channel_index = -1

# ----- Establishing WiFi connection -----#

# Connecting to WiFi (Faculty WiFi configuration)
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("Ugradbeni", "USlaboratorija220")
while not sta_if.isconnected():
    pass
print("Wi-Fi je povezan!")

# Defining a unique client name for MQTT connection
MQTT_CLIENT_NAME = "UsProject"

# Initialization of MQTT client and connectig to broker adress
mqtt_client = MQTTClient(MQTT_CLIENT_NAME, "broker.hivemq.com")
mqtt_client.connect()

# Function used for clearing all the fields on display by calling
# modified print method on display object (needed to be modified
# because the default print from library doesn't have the option to print spaces)


def erase_fields_from_display():
    display.set_pos(display.width-190, 17)
    display.print_with_spaces("                                           ")
    display.set_pos(display.width-190, 57)
    display.print_with_spaces("                                           ")
    display.set_pos(display.width-190, 97)
    display.print_with_spaces("                                           ")

# Function that clears the values from display and displays new ones based on the channel
# object provided as a parameter
count = 0

def display_channel(channel_to_be_displayed):
    global count
    print("here " + str(count))
    count += 1
    erase_fields_from_display()
    if channel_list:
        display.set_pos(display.width-190, 17)
        display.print(channel_to_be_displayed.name)
        display.set_pos(display.width-190, 57)
        display.print(format_number_with_separators(
            channel_to_be_displayed.views))
        display.set_pos(display.width-190, 97)
        display.print(format_number_with_separators(
            channel_to_be_displayed.subs))

# Function responsible for handling any messages that are being published on predefined themes
def sub(topic, msg):
    global current_channel_index
    
    if topic == b'UsProject/channel/add':
        data = json.loads(msg.decode())
        name = data["name"]
        views = data["viewCount"]
        subs = data["subscriberCount"]

        channel = Channel(name, views, subs)
        channel_list.append(channel)

        # This is triggered only when the channel_list is empty
        if current_channel_index == -1:
            display_channel(channel_list[0])
            current_channel_index += 1
        pass

    # Resets display and channel_list
    elif topic == b'UsProject/channel/removeAll':
        channel_list.clear()
        erase_fields_from_display()
        current_channel_index = -1
        pass

    elif topic == b'UsProject/channel/remove':
        data = json.loads(msg.decode())
        name = data["name"]
        views = data["viewCount"]
        subs = data["subscriberCount"]

        channel = Channel(name, views, subs)
        found_channel = None
        deletingPosition = 0

        # Searching the published channel and its position in channel_list
        for i, c in enumerate(channel_list):
            if c.name == channel.name:
                found_channel = c
                deletingPosition = i
                break

        if found_channel:
            if current_channel_index == deletingPosition:
                channel_list.remove(found_channel)
                # Entering when we want to delete the channel that is currently being showed
                # In this case we would stay on the same position and update the displayed values
                # with the Channel that was next to the removed one
                if len(channel_list) != 0:
                    current_channel_index = (
                        current_channel_index) % len(channel_list)
                    display_channel(channel_list[current_channel_index])
                # If we deleted the one and only element of the list the display values are
                # completely removed
                else:
                    erase_fields_from_display()
                    current_channel_index = -1
            else:
                channel_list.remove(found_channel)
                # Adjust the current_channel_index if it was pointing to the removed channel
                if current_channel_index > deletingPosition:
                    current_channel_index -= 1


# Subscription to themes and setting callback function
mqtt_client.set_callback(sub)
mqtt_client.subscribe(b"UsProject/channel/add")
mqtt_client.subscribe(b"UsProject/channel/removeAll")
mqtt_client.subscribe(b"UsProject/channel/remove")

# ----- Display setup -----#

# Display const dimensions
SCR_WIDTH = const(320)
SCR_HEIGHT = const(240)
SCR_ROT = const(2)
CENTER_Y = int(SCR_WIDTH/2)
CENTER_X = int(SCR_HEIGHT/2)

# Setting SPI communication with display
TFT_CLK_PIN = const(18)
TFT_MOSI_PIN = const(19)
TFT_MISO_PIN = const(16)
TFT_CS_PIN = const(17)
TFT_RST_PIN = const(20)
TFT_DC_PIN = const(15)

spi = SPI(
    0,
    baudrate=62500000,
    miso=Pin(TFT_MISO_PIN),
    mosi=Pin(TFT_MOSI_PIN),
    sck=Pin(TFT_CLK_PIN))

display = ILI9341(
    spi,
    cs=Pin(TFT_CS_PIN),
    dc=Pin(TFT_DC_PIN),
    rst=Pin(TFT_RST_PIN),
    w=SCR_WIDTH,
    h=SCR_HEIGHT,
    r=3)

# Set up of needed colors
white = color565(255, 255, 255)
red = color565(255, 0, 0)
black = color565(0, 0, 0)

display.set_font(tt14)

# ----- Loading screen -----#

# Clearing display on start
display.erase()

display.set_color(white, red)

# Draw the YouTube play button
x0, y0 = 100 + 20, 100 - 30  # Upper point
x1, y1 = 100 + 20, 190 - 30  # Lower point
x2, y2 = 200 + 20, 145 - 30  # Right point

display.fill_rectangle(0, 0, display.width, display.height, red)
#display.draw_triangle(x0, y0, x1, y1, x2, y2, white)
display.fill_triangle(x0, y0, x1, y1, x2, y2, white)
display.set_pos(70, 200)
display.print("YouTube Subscriber Counter")

# Wait for a few seconds
time.sleep(2)

# ----- Main screen -----#

# Set new font colors


# Main Background creation
display.fill_rectangle(0, 0, display.width, display.height, white)
display.fill_rectangle(0, 0, display.width-200, display.height, red)

# Draw the small YouTube play button
x0, y0 = 45, 100      # Upper point
x1, y1 = 45, 140      # Lower point
x2, y2 = 80, CENTER_X  # Right point
#display.draw_triangle(x0, y0, x1, y1, x2, y2, white)
display.fill_triangle(x0, y0, x1, y1, x2, y2, white)

display.set_color(red, white)
# Set the templated text
display.set_pos(display.width-190, 5)
display.print("Current Channel:")

display.set_pos(display.width-190, 45)
display.print("Number of Views:")

display.set_pos(display.width-190, 85)
display.print("Number of Subscribers:")

display.set_color(black, white)

display.set_pos(display.width-190, 155)
display.print("Next Channel (BTN0)")

display.set_pos(display.width-190, 175)
display.print("Previous Channel (BTN1)")

display.set_pos(display.width-190, 195)
display.print("Remove Current (BTN2)")

display.set_pos(display.width-190, 215)
display.print("Remove All (BTN3)")

# ----- Button handling setup -----#

# This function recieves a number in format '123456789' and returns the number as string
# in a more natural format with spaces "123 456 789"


def format_number_with_separators(number):
    number_str = str(number)
    formatted_str = ""
    count = 0

    # Iterate over the characters in reverse order
    for char in reversed(number_str):
        if count != 0 and count % 3 == 0:
            # Insert a space every three characters
            formatted_str = " " + formatted_str

        formatted_str = char + formatted_str
        count += 1

    return formatted_str

# This function handles button press event

debounce = 0

def button0_handler(pin):
    global current_channel_index, debounce
    if time.ticks_diff(time.ticks_ms(), debounce) < 200:
        return
    debounce = time.ticks_ms()
    # Increment the current channel index only if the list is not empty and
    # display the new current channel attriubutes
    if channel_list:
        current_channel_index = (current_channel_index + 1) % len(channel_list)
        display_channel(channel_list[current_channel_index])

def button1_handler(pin):
    global current_channel_index, debounce
    if time.ticks_diff(time.ticks_ms(), debounce) < 200:
        return
    debounce = time.ticks_ms()
    # Increment the current channel index only if the list is not empty and
    # display the new current channel attriubutes
    if channel_list:
        current_channel_index = (current_channel_index - 1) % len(channel_list)
        display_channel(channel_list[current_channel_index])

def button2_handler(pin):
    global current_channel_index, debounce
    if time.ticks_diff(time.ticks_ms(), debounce) < 200:
        return
    debounce = time.ticks_ms()
    # Increment the current channel index only if the list is not empty and
    # display the new current channel attriubutes
    if channel_list:
        channel_list.remove(channel_list[current_channel_index])
        mqtt_client.publish(b'UsProject/channel/sendToMobile', "removeCurrent".encode())
        if channel_list:
            current_channel_index = (current_channel_index - 1) % len(channel_list)
            display_channel(channel_list[current_channel_index]) 
        else:
            erase_fields_from_display()
            current_channel_index = -1

def button3_handler(pin):
    global current_channel_index, debounce
    if time.ticks_diff(time.ticks_ms(), debounce) < 200:
        return
    debounce = time.ticks_ms()
    # Increment the current channel index only if the list is not empty and
    # display the new current channel attriubutes
    if channel_list:
        channel_list.clear()
        erase_fields_from_display()
        current_channel_index = -1
        mqtt_client.publish(b'UsProject/channel/sendToMobile', "removeAll".encode())

# Set up the button interrupt
button0.irq(trigger=Pin.IRQ_FALLING, handler=button0_handler)
button1.irq(trigger=Pin.IRQ_FALLING, handler=button1_handler)
button2.irq(trigger=Pin.IRQ_FALLING, handler=button2_handler)
button3.irq(trigger=Pin.IRQ_FALLING, handler=button3_handler)

# ----- Main code -----#
mqtt_client.publish(b'UsProject/channel/startup', str(1).encode())
# Infinite while loop that watches if anything is published on subscribed themes
while True:
    mqtt_client.wait_msg()
