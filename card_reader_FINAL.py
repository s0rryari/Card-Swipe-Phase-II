import time
from mfrc522 import MFRC522	#for MFRC522
import RPi.GPIO as GPIO		#for leds
import os					#used for copying onto flash drive
import shutil				#used for copying onto flash drive
from datetime import datetime	#for time stamps

#--------LED SETUP------------------------		
#setting GPIO pins of LEDs					
led_green = 18 
led_red = 17

#set GPIOS to output mode
GPIO.setmode(GPIO.BCM)
GPIO.setup(led_green, GPIO.OUT)
GPIO.setup(led_red, GPIO.OUT)
#------------------------------------------

#---------------FLASHDRIVE COPYING SETUP--------------------------------------------------------------------------------
WATCH_FOLDER = "/media/xproject"  							#folder containing USB mount point that detects if a flashdrive has been inserted
TEXT_FILE_PATH = "/home/xproject/Documents/readings.txt"  	# Path to the file to copy (text file that contains RFID readings)
#-----------------------------------------------------------------------------------------------------------------------

#---------TEXT FILE SETUP----------------
f = open("readings.txt", "a")	
f.write("\n\nnew data\n")		#header written on boot
f.close()						
#----------------------------------------

#----------MFRC522 READER SETUP------------------------
reader = MFRC522()	# Initialize MFRC522 Reader

# Constants
MAX_UIDS = 100  	# Maximum number of unique UIDs to track

# Data Storage
scanned_UIDs = []  # array to store unique UIDs
total_scans = 0    # Counter for total scans
#-------------------------------------------------------

#-----------------FUNCTIONS FOR SCANNING IDS--------------------------------
def get_UID():
    """Reads the RFID tag and returns its UID as a string."""
    reader.MFRC522_Request(reader.PICC_REQIDL)  	# Look for cards
    status, uid_data = reader.MFRC522_Anticoll()  # Read card serial

    if status == reader.MI_OK:				#card detected		
	    GPIO.output(led_red,GPIO.LOW)		
	    GPIO.output(led_green, GPIO.HIGH)	
	    time.sleep(1)						#keep green led on for 1 second to indicate successful card reading 
	    GPIO.output(led_green, GPIO.LOW)	
	    GPIO.output(led_red, GPIO.HIGH)		 
	    uid_str = "-".join([str(byte) for byte in uid_data])	#convert UID information into string
	    return uid_str
    return None	

def add_UID(UID):
    """Adds a UID to the list if it's unique."""
    global scanned_UIDs
    if UID not in scanned_UIDs:
        if len(scanned_UIDs) < MAX_UIDS:	#if not at max capacity of UIDs
            scanned_UIDs.append(UID)		#append new UID to array
        else:
            print("Error: UID storage limit reached!")	

def print_scan_details(UID, unique_index):	#printing to terminal (for debugging/testing)
    """Prints scan details with UID and index."""
    print(f"Total Scans: {total_scans}, Unique Scan ({unique_index}): {UID}")
#------------------------------------------------------------------------------

#----------FUNCTIONS FOR FLASHDRIVE COPYING------------------------------------
def get_usb_mount():
    """Returns the first detected USB mount point."""
    for folder in os.listdir(WATCH_FOLDER): #looping through all files/folders in WATCH_FOLDER
        mount_path = os.path.join(WATCH_FOLDER, folder)	#building full path first mounted device found inside watch_folder
        if os.path.ismount(mount_path):	#checking if an actual device is mounted
            return mount_path
    return None

def copy_to_usb():
    """Copies the text file to the inserted USB drive."""
    mount_point = get_usb_mount()
    if mount_point:
	    dest_path = os.path.join(mount_point, os.path.basename(TEXT_FILE_PATH))	#creating file path that combines mount_point file path and file name of the text file
	    shutil.copy(TEXT_FILE_PATH, dest_path)	#copying text file from source path to destination path (doing both reading and writing of source file)
	    
		#blinking green led to indicate copying of data
	    GPIO.output(led_green,GPIO.LOW)
	    time.sleep(.2)
	    GPIO.output(led_green,GPIO.HIGH)
	    time.sleep(.2)
	    GPIO.output(led_green,GPIO.LOW)
	    time.sleep(.2)
	    GPIO.output(led_green,GPIO.HIGH)
	    time.sleep(.2)
	    GPIO.output(led_green,GPIO.LOW)
#--------------------------------------------------------

def main():
    global total_scans

    GPIO.output(led_red, GPIO.HIGH)	#turn on red led and keep it on until successful scan

    print("\n\nReady to scan cards...")	#for debugging/testing

    try:
	    while True:
	    #check for flash drive first
		    if get_usb_mount():
			    GPIO.output(led_green, GPIO.HIGH)	#both leds on to indicate flash drive detected
			    time.sleep(2)
			    copy_to_usb()
			    time.sleep(5)  # Prevent multiple rapid copies

		    UID = get_UID()	#convert UID to string
	    			
		    if UID:
			    total_scans += 1 
			    unique_index = scanned_UIDs.index(UID) + 1 if UID in scanned_UIDs else len(scanned_UIDs) + 1	#if UID is NOT unique, obtaining its unique index from scanned_UIDs, else create a new unique index for the UID

			    if UID not in scanned_UIDs:		#if UID unique, add to scanned_UIDS
				    add_UID(UID)

			    print_scan_details(UID, unique_index)	#printing to terminal (for debugging/testing)
			    #-----Writing data to text file------------
			    f = open("readings.txt", "a")							
			    timestamp=datetime.now().strftime("%Y-%m-%d %I:%M %p")	#create time stamp
			    f.write(f"{timestamp}	Total Scans: {total_scans}, Unique Scan ({unique_index}): {UID}\n")	#what's written to file everytime a card is scanned: timestamp, total scans, unique index, and the UID string
			    f.close()	
				#------------------------------------------

		    time.sleep(1)  # Avoid multiple detections from the same scan

    except KeyboardInterrupt:
        print("\nExiting program...")
        reader.MFRC522_StopCrypto1()

if __name__ == "__main__":
    main()
