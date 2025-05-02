# Card-Swipe-Phase-II
This project is designed for a university ID card reader system. It reads card data via RFID, extracts the UID, and logs the information to a text file. The system also provides user feedback through GPIO-controlled indicators (e.g., LEDs) to signal successful or unsuccessful card reads, as well as successful data copying to a flash drive.

Additional feature:
-Automatic USB Backup: When a flash drive is inserted, the system automatically copies the text file containing the scan logs to the drive (used for testing purposes)

Each card scan log includes:
-Timestamp of the scan
-Total number of scans
-Unique ID (used to distinguish new vs. returning users)
-UID string of the scanned card
