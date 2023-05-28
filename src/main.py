import time
import utime
from machine import Pin, PWM

from config import NETWORK_PASS, NETWORK_SSID, API_PATH
from button import Button
from lifelog_service import LifelogService

status_led_pin = Pin("LED", Pin.OUT)
llsvc = None

# the pins to which the buttons are connected and the order
# in which they should be assigned to the outgoing press
button_pins = [3, 7, 11, 15, 16, 20]
buttons = []

def connect_wlan():
    global llsvc

    llsvc = LifelogService(NETWORK_SSID, NETWORK_PASS, API_PATH)
    llsvc.connect()

    connect_wait_seconds = 60
    status_led_pin.toggle()

    while connect_wait_seconds > 0:
        if llsvc.is_connected():
            break
        connect_wait_seconds -= 1
        status_led_pin.toggle()
        time.sleep(1)

    status_led_pin.value(1)

def handle_button_press(pin):
    # loop through the buttons to find the one that raised the interrupt
    for button in buttons:
        if button.handle_interrupt(pin):
            print(f'Button press on {button.button_id}')
            break

def init_buttons():
    global button_pins

    i = 0
    for pin_id in button_pins:
        buttons.append(Button(pin_id, i, irq_handler=handle_button_press))
        i += 1

def init():
    connect_wlan()
    init_buttons()
    main_loop()

def main_loop():
    global llsvc

    while True:
        for button in buttons:
            button.handle_tick(utime.ticks_ms())
            if button.should_send_event():
                llsvc.send_event(button.button_id)

init()
