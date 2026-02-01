#!/usr/bin/python
import time
import RPi.GPIO as GPIO
import dht11 as d

# Zuordnung der GPIO Pins
LCD_RS = 4
LCD_E  = 17
LCD_DATA4 = 18
LCD_DATA5 = 22
LCD_DATA6 = 23
LCD_DATA7 = 24
dhtpin = 25
LED = 5
PIEP = 6
switch = 26

HI = GPIO.HIGH
LO = GPIO.LOW
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIEP, GPIO.OUT)
buzzer=GPIO.PWM(PIEP, 600)
GPIO.setup(switch, GPIO.IN)
GPIO.setup(LED, GPIO.OUT, initial=LO)

LCD_WIDTH = 16 		# Zeichen je Zeile
LCD_LINE_1 = 0x80 	# Adresse der ersten Display Zeile
LCD_LINE_2 = 0xC0 	# Adresse der zweiten Display Zeile
LCD_CHR = HI
LCD_CMD = LO
E_PULSE = 0.0005
E_DELAY = 0.0005
tempsensor = d.DHT11(pin=dhtpin)				# Nutzung der DHT11 Library

def lcd_send_byte(bits, mode):					# LCD Bitfunktionen für 8-Bit Datenübergabe auf 4 Datenpins 
	# Pins auf LOW setzen
	GPIO.output(LCD_RS, mode)
	GPIO.output(LCD_DATA4, LO)
	GPIO.output(LCD_DATA5, LO)
	GPIO.output(LCD_DATA6, LO)
	GPIO.output(LCD_DATA7, LO)
	if bits & 0x10 == 0x10:
		GPIO.output(LCD_DATA4, HI)
	if bits & 0x20 == 0x20:
		GPIO.output(LCD_DATA5, HI)
	if bits & 0x40 == 0x40:
		GPIO.output(LCD_DATA6, HI)
	if bits & 0x80 == 0x80:
		GPIO.output(LCD_DATA7, HI)
	time.sleep(E_DELAY)    
	GPIO.output(LCD_E, HI)  
	time.sleep(E_PULSE)
	GPIO.output(LCD_E, LO)  
	time.sleep(E_DELAY)      
	GPIO.output(LCD_DATA4, LO)
	GPIO.output(LCD_DATA5, LO)
	GPIO.output(LCD_DATA6, LO)
	GPIO.output(LCD_DATA7, LO)
	if bits&0x01==0x01:
		GPIO.output(LCD_DATA4, HI)
	if bits&0x02==0x02:
		GPIO.output(LCD_DATA5, HI)
	if bits&0x04==0x04:
		GPIO.output(LCD_DATA6, HI)
	if bits&0x08==0x08:
		GPIO.output(LCD_DATA7, HI)
	time.sleep(E_DELAY)    
	GPIO.output(LCD_E, HI)  
	time.sleep(E_PULSE)
	GPIO.output(LCD_E, LO)  
	time.sleep(E_DELAY)  

def display_init():
	lcd_send_byte(0x33, LCD_CMD)
	lcd_send_byte(0x32, LCD_CMD)
	lcd_send_byte(0x28, LCD_CMD)
	lcd_send_byte(0x0C, LCD_CMD)  
	lcd_send_byte(0x06, LCD_CMD)
	lcd_send_byte(0x01, LCD_CMD)  

def lcd_message(message):
	message = message.ljust(LCD_WIDTH," ")  
	for i in range(LCD_WIDTH):
	  lcd_send_byte(ord(message[i]),LCD_CHR)
	
def nachricht(msg1, msg2):						# Funktion zur Ausgabe auf LCD mit Parameterübernahme
	display_init()


	for i in range(len(msg1)):
		lcd_send_byte(LCD_LINE_1, LCD_CMD)
		lcd_message(msg1[:i+1])
		lcd_send_byte(LCD_LINE_2, LCD_CMD)
		lcd_message("")
		
	for i in range(len(msg2)):
		lcd_send_byte(LCD_LINE_1, LCD_CMD)
		lcd_message(msg1)
		lcd_send_byte(LCD_LINE_2, LCD_CMD)
		lcd_message(msg2[:i+1])
		
if __name__ == '__main__':						# Start des Programmes
	# initialisieren
	GPIO.setmode(GPIO.BCM)
	GPIO.setwarnings(False)
	GPIO.setup(LCD_E, GPIO.OUT)
	GPIO.setup(LCD_RS, GPIO.OUT)
	GPIO.setup(LCD_DATA4, GPIO.OUT)
	GPIO.setup(LCD_DATA5, GPIO.OUT)
	GPIO.setup(LCD_DATA6, GPIO.OUT)
	GPIO.setup(LCD_DATA7, GPIO.OUT)
	GPIO.setup(LED, GPIO.OUT, initial=LO)
	nachricht(f"Funktions", f"Test")
	GPIO.output(LED, HI)
	buzzer.start(30)
	time.sleep(0.2)
	GPIO.output(LED, LO)
	buzzer.stop()
	time.sleep(0.2)
	GPIO.output(LED, HI)
	buzzer.start(30)
	time.sleep(0.2)
	GPIO.output(LED, LO)
	buzzer.stop()

	einheittoggle = "Celsius"
	
	try:
		while True:
			result = tempsensor.read()
			
			if GPIO.input(switch) == 0:						# Schalter-Status zur Temperatureinheitsänderung
				if einheittoggle == "Celsius":
					einheittoggle = "Fahrenheit"
					nachricht("Umgeschaltet auf", "Fahrenheit")		# Ausgabe auf dem LCD Display
				else:
					einheittoggle = "Celsius"
					nachricht("Umgeschaltet auf", "Celsius")

			print("SW Status: " + str(GPIO.input(switch)) + einheittoggle) # Ausgabe auf Konsole (Debug)
			time.sleep(2)
			if result.is_valid():			# Check ob der DHT11 Gültige Daten liefert
				if einheittoggle == "Celsius":
					nachricht(f"Temp: {result.temperature} \u00DFC", f"Luftf: {result.humidity} %") # Werteausgabe auf LCD, Das LCD gibt bei für formatstring (f) das ß das ° Zeichen aus
				else:
					nachricht(f"Temp: {round((result.temperature * 1.8 + 32), 1)} \u00DFF", f"Luftf: {result.humidity} %")	# (f"") in der Ausgabe für formatstring
				if result.temperature >= 26:				# Temperaturcheck über 26°C
					GPIO.output(LED, HI)					# Anschalten der LED
					buzzer.start(50)						# Anschalten des Buzzers
					time.sleep(0.5)
					GPIO.output(LED, LO)					# Ausschalten der LED
					buzzer.stop()							# Ausschalten des Buzzers
					time.sleep(0.5)
					GPIO.output(LED, HI)
					buzzer.start(50)
					time.sleep(0.5)
					GPIO.output(LED, LO)
					buzzer.stop()
					time.sleep(0.5)
					GPIO.output(LED, HI)
					buzzer.start(50)
					time.sleep(0.5)
					GPIO.output(LED, LO)
					buzzer.stop()
					time.sleep(2)
					if einheittoggle == "Celsius":			# Check der gewählten Temperatureinheit
						nachricht(f"WARNUNG: Hohe", "Temp >26\u00DFC")
					else:
						nachricht(f"WARNUNG: Hohe", "Temp >78,8\u00DFF")
				if result.humidity >= 50:					# Check der Luftfeuchtigkeit
					GPIO.output(LED, HI)
					buzzer.start(50)
					time.sleep(0.5)
					GPIO.output(LED, LO)
					buzzer.stop()
					time.sleep(0.5)
					GPIO.output(LED, HI)
					buzzer.start(50)
					time.sleep(0.5)
					GPIO.output(LED, LO)
					buzzer.stop()
					time.sleep(0.5)
					GPIO.output(LED, HI)
					buzzer.start(50)
					time.sleep(0.5)
					GPIO.output(LED, LO)
					buzzer.stop()
					time.sleep(2)
					nachricht(f"WARNUNG: Hohe", f"Luftfeuchte >50%")
				print(f"Temperatur: {result.temperature} °C, Luftfeuchte: {result.humidity}%")	# Ausgabe auf Konsole (Debug)
			else:
				print(f"Ungueltiges Ergebnis")
			time.sleep(2)
	
	finally:
		print("Bye")
		GPIO.cleanup()