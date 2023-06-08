from ili934xnew import ILI9341, color565
from machine import Pin, SPI, ADC
from micropython import const
import os
import glcdfont
import tt14
import tt24
import tt32
import time

import network
from umqtt.robust import MQTTClient
from machine import Pin, ADC, PWM, Timer
import time
import json









# Define the button pin
button_pin = Pin(0, Pin.IN, Pin.PULL_UP)

adc=ADC(Pin(28))

# Defining Channel class
class Channel:
    def __init__(self, name, views, subs):
        self.name = name
        self.views = views
        self.subs = subs
   
    def print_values(self):
        print("name:", self.name)
        print("views:", self.views)
        print("subs:", self.subs)

































# Povezivanje na Wi-Fi mrežu
sta_if = network.WLAN(network.STA_IF)
sta_if.active(True)
sta_if.connect("Ugradbeni", "USlaboratorija220")
while not sta_if.isconnected():
    pass
print("Wi-Fi je povezan!")





























# Define a list to store the channel objects
channel_list = []

# Define the current channel index
current_channel_index = 0

# Definisanje naziva klijenta
MQTT_CLIENT_NAME = "UsProject"

# Inicijalizacija MQTT klijenta i konekcija na broker
mqtt_client = MQTTClient(MQTT_CLIENT_NAME, "broker.hivemq.com")
mqtt_client.connect()

def clearFieldsOnDisplay():
    display.set_pos(display.width-190,17)
    display.printEmanVerzija("                            ")
    display.set_pos(display.width-190,57)
    display.printEmanVerzija("                            ")
    display.set_pos(display.width-190,97)
    display.printEmanVerzija("                            ")
   
def fillFieldsOnDisplay(displayChannel):
    clearFieldsOnDisplay()
    display.set_pos(display.width-190,17)
    if channel_list:
        display.print(displayChannel.name)
    display.set_pos(display.width-190,57)
    if channel_list:
        display.print(format_number_with_separators(displayChannel.views))
    display.set_pos(display.width-190,97)
    if channel_list:
        display.print(format_number_with_separators(displayChannel.subs))
       

def sub(topic, msg):
    print("Received message on topic:", topic)
    print("Payload:", msg)

    if topic == b'UsProject/channel/add':
        data = json.loads(msg.decode())
        name = data["name"]
        views = data["viewCount"]
        subs = data["subscriberCount"]

        channel = Channel(name, views, subs)
        channel.print_values()
        channel_list.append(channel)
        pass
    if topic == b'UsProject/channel/removeAll':
        channel_list.clear()
        clearFieldsOnDisplay()
        pass
    elif topic == b'UsProject/channel/remove':
        data = json.loads(msg.decode())
        name = data["name"]
        views = data["viewCount"]
        subs = data["subscriberCount"]

        channel = Channel(name, views, subs)
        found_channel = None
        deletingPosition = -1

        for i, c in enumerate(channel_list):
            if c.name == channel.name:
                found_channel = c
                deletingPosition = i
                break

        if found_channel:
            print("Found channel:", found_channel.name)
            #ODAVDE NIJE OK
            if current_channel_index == deletingPosition:
                current_channel_index = (current_channel_index + 1) % len(channel_list)
                fillFieldsOnDisplay(channel_list[0])
                channel_list.remove(found_channel)
            else:
                # Adjust the current_channel_index if it was pointing to the removed channel
                if current_channel_index > 0:
                    current_channel_index -= 1
                    fillFieldsOnDisplay(channel_list[current_channel_index])


# Postavljanje funkcije za obradu poruka na MQTT klijentu i pretplata na teme
mqtt_client.set_callback(sub)
mqtt_client.subscribe(b"UsProject/channel/add")
mqtt_client.subscribe(b"UsProject/channel/removeAll")
mqtt_client.subscribe(b"UsProject/channel/remove")



#print("Before publish")
#mqtt_client.publish(b"UsProject/channel/add", "picoETF")
#print("After publish")



































# Dimenzije displeja
SCR_WIDTH = const(320)
SCR_HEIGHT = const(240)
SCR_ROT = const(2)
CENTER_Y = int(SCR_WIDTH/2)
CENTER_X = int(SCR_HEIGHT/2)

# Podešenja SPI komunikacije sa displejem
TFT_CLK_PIN = const(18)
TFT_MOSI_PIN = const(19)
TFT_MISO_PIN = const(16)
TFT_CS_PIN = const(17)
TFT_RST_PIN = const(20)
TFT_DC_PIN = const(15)

# Fontovi na raspolaganju
fonts = [glcdfont,tt14,tt24,tt32]
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

# Set up colors
white = color565(255, 255, 255)
red = color565(255, 0, 0)
black = color565(0, 0, 0)

display.set_font(fonts[1])

# Clear the display
display.erase()

#Loading screen

display.set_color(white,red)

# Draw the YouTube play button
x0, y0 = 100 + 20, 100 - 30 #gornji vrh
x1, y1 = 100 + 20, 190 - 30 #donji vrh
x2, y2 = 200 + 20, 145 - 30 #desni vrh

display.fill_rectangle(0, 0, display.width, display.height, red)
display.draw_triangle(x0, y0, x1, y1, x2, y2, white)
display.fill_triangle(x0, y0, x1, y1, x2, y2, white)
display.set_pos(70,200)
display.print("YouTube Subscriber Counter")

# Wait for a few seconds
time.sleep(2)

# Set new font colors
display.set_color(black,white)

#Main Background creation
display.fill_rectangle(0, 0, display.width, display.height, white)
display.fill_rectangle(0, 0, display.width-200, display.height, red)

# Draw the YouTube play button
x0, y0 = 45, 100 #gornji vrh
x1, y1 = 45, 140 #donji vrh
x2, y2 = 80, CENTER_X #desni vrh
display.draw_triangle(x0, y0, x1, y1, x2, y2, white)
display.fill_triangle(x0, y0, x1, y1, x2, y2, white)

display.set_pos(display.width-190,5)
display.print("Selected Channel:")

display.set_pos(display.width-190,45)
display.print("Number of Views:")

display.set_pos(display.width-190,85)
display.print("Number of Subscribers:")

display.set_pos(display.width-100,200)
display.print("Next Channel (press button)")

#time.sleep(200)

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

# Define a function to handle button press event
def button_press_handler(pin):
    global current_channel_index

    if channel_list:
        fillFieldsOnDisplay(channel_list[current_channel_index])

    # Increment the current channel index only if the list is not empty
    if channel_list:
        current_channel_index = (current_channel_index + 1) % len(channel_list)

#Set up the button interrupt
button_pin.irq(trigger=Pin.IRQ_FALLING, handler=button_press_handler)

while True:
    mqtt_client.wait_msg()