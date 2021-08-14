#!/usr/bin/python
'''
Raspberry Pi Bluetooth Proximity Unlocker

Usage: You must pass the Bluetooth MAC address of the "key" device as the
first command line argument.

    python pi-bluetooth-proximity-unlocker.py AB:CD:EF:12:34:56

This was developed and tested on a RaspberryPi Zero W using the BC Robotics
2 channel relay Pi Zero hat
https://bc-robotics.com/shop/raspberry-pi-zero-relay-hat/
It also should work for any relay hat or breakout board if you change the
GPIO pins accordingly.

This depends on bluetooth, install it with the following command.
sudo apt-get install --no-install-recommends bluetooth

Proximity delay variable.
Defaults to 5 seconds. L2ping takes approx 5 seconds so the prox_delay
variable only adds to that delay.

GPIO delay variable.
Defaults to .25 seconds.
This is a reasonable delay for most button press simulations.

'''


# Imports
import sys
import argparse
import re
import time
import RPi.GPIO as GPIO
import subprocess


#  Argument parser setup
parser = argparse.ArgumentParser("pi-bluetooth-proximity-unlocker.py")
parser.add_argument("phone_mac", help="You must pass the Bluetooth MAC address \
    of the 'key' device as the first command line argument. EX. \n\
        python pi-bluetooth-proximity-unlocker.py AB:CD:EF:12:34:56", type=str)
parser.add_argument('--prox_delay', type=int, help='Optional\nProximity delay variable. \
    Defaults to 5 seconds. L2ping takes approx 5 seconds so the prox_delay \
        variable only adds to that delay.', default=5, required=False)
parser.add_argument('--gpio_delay', type=int, help='Optional\nGPIO delay variable. \
    Defaults to .25 seconds. This is a reasonable delay for most button press \
        simulations.', default=.25, required=False)
args = parser.parse_args()


def valid_mac(phone_mac):
    '''
    Key device MAC address validation.
    Takes in MAC address as a string with : or - delimination.
    Validates MAC with regex.
    Exits on invalid MAC address.
    Returns phone_mac string.
    '''
    #  MAC regex
    regex = ("^([0-9A-Fa-f]{2}[:-])" +
             "{5}([0-9A-Fa-f]{2})|" +
             "([0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4}\\." +
             "[0-9a-fA-F]{4})$")

    #  Compile the regex
    p = re.compile(regex)

    #  Validate MAC
    if(re.search(p, phone_mac)):
        return phone_mac
    else:
        sys.exit("Invalid MAC address. Please retry with this format\nAB:CD:EF:12:34:56")


# Phone MAC, delay, and GPIO settings
phone_mac = valid_mac(args.phone_mac)  # Bluetooth MAC of"key" device

gpio_delay = args.gpio_delay  # Set the delay between GPIO commands
prox_delay = args.prox_delay  # Set the delay between phone proximity searches

GPIO.setmode(GPIO.BCM)  # Sets the Broadcom pin-numbering scheme for GPIO pins
GPIO.setwarnings(False)  # Suppresses GPIO warnings
GPIO.setup(4, GPIO.OUT)  # Set Relay 1 GPIO output pin
GPIO.setup(17, GPIO.OUT)  # Set Relay 2 GPIO output pin


def phone_check(phone_mac):
    '''
    Takes in a phone mac address as a string and uses subprocess and l2ping to
    check for phone proximity
    Returns the phone_prox variable as a boolean
    '''
    try:
        subprocess.check_output(
            "sudo l2ping -c 1 -t 1 {}".format(phone_mac),
            stderr=subprocess.STDOUT, shell=True)
        print("Phone MAC found!")
        phone_prox = True
        return phone_prox
    except subprocess.CalledProcessError:
        print("Phone MAC not found!")
        phone_prox = False
        return phone_prox


def lock_doors():
    '''
    Locks doors via relay actuation
    Returns the doors_locked variable as a boolean
    Simulates two button presses
    '''
    GPIO.output(4, GPIO.HIGH)  # turn relay 1 on
    time.sleep(gpio_delay)
    GPIO.output(4, GPIO.LOW)  # turn relay 1 off
    time.sleep(gpio_delay)
    GPIO.output(4, GPIO.HIGH)  # turn relay 1 on
    time.sleep(gpio_delay)
    GPIO.output(4, GPIO.LOW)  # turn relay 1 off
    doors_locked = True
    print("Locking Doors!")
    return doors_locked


def unlock_doors():
    '''
    Unlocks doors via relay actuation
    Returns the doors_locked variable as a boolean
    Simulates two button presses
    '''
    GPIO.output(17, GPIO.HIGH)  # turn relay 2 on
    time.sleep(gpio_delay)
    GPIO.output(17, GPIO.LOW)  # turn relay 2 off
    time.sleep(gpio_delay)
    GPIO.output(17, GPIO.HIGH)  # turn relay 2 on
    time.sleep(gpio_delay)
    GPIO.output(17, GPIO.LOW)  # turn relay 2 off
    doors_locked = False
    print("Unlocking Doors!")
    return doors_locked


# Infinite while loop checking phone proximity status and door lock status
print("Setting initial conditions and starting proximity scan!")
doors_locked = unlock_doors()  # Set initial conditions
while True:
    if phone_check(phone_mac) is True and doors_locked is True:
        doors_locked = unlock_doors()
        time.sleep(prox_delay)
    if phone_check(phone_mac) is True and doors_locked is False:
        time.sleep(prox_delay)
    if phone_check(phone_mac) is False and doors_locked is False:
        doors_locked = lock_doors()
        time.sleep(prox_delay)
    if phone_check(phone_mac) is False and doors_locked is True:
        time.sleep(prox_delay)
