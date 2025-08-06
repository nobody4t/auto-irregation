# Automated Irrigation System - Setup Guide 🌱

This system automatically waters your plants, monitors temperature and humidity, detects animals, and provides a web interface to control everything from your phone or computer.

## ⚠️ IMPORTANT HARDWARE WARNING ⚠️

**READ THIS BEFORE CONNECTING ANYTHING:**

![Setup Warning](attention.png)

- **Water pump and soil sensor connections look identical - DO NOT mix them up**
- **Connect ALL wires and modules FIRST, then connect power LAST**

## What You'll Get

- 🌡️ Temperature and humidity monitoring
- 💧 Automatic plant watering
- 📱 Web control from any device
- 🐰 Animal detection with camera
- 📊 Data logging and reports
- 🎥 Live video stream

## Hardware Setup

Follow the wiring diagram exactly:

![Hardware Wiring Diagram](hardware.png)

Connect in this order:

1. Camera module to Pi
2. Soil sensor to GPIO pins
3. Relay module to GPIO pins
4. Water pump to relay
5. Network cable
6. **Power connection LAST**

---

## Software Installation

**Just copy and paste each command one by one into your Pi's terminal.**

### Step 1: Install Basic System Requirements

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install python3.11 python3.11-venv python3.11-dev -y
sudo apt install python3-pip git -y
pip3 install gpiozero adafruit-circuitpython-dht paho-mqtt
sudo apt install libgpiod2
```

### Step 2: Download the Project

```bash
git clone https://github.com/nobody4t/auto-irregation.git
cd auto-irrigation
```

### Step 3: Install Additional System Requirements

```bash
sudo apt update
sudo apt upgrade -y
sudo apt install mysql-server libmysqlclient-dev -y
sudo apt install build-essential pkg-config -y
sudo apt install python3-picamera2 python3-rpi.gpio -y
curl -sS https://bootstrap.pypa.io/get-pip.py | python3.11
```

### Step 4: Create Python Environment

```bash
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Setup Database

```bash
sudo systemctl start mysql
sudo systemctl enable mysql
sudo mysql -u root -p
```

**When MySQL opens, copy and paste these commands one by one:**

```sql
CREATE DATABASE grass_database;
CREATE USER 'root'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON grass_database.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 6: Initialize the System

```bash
python manage.py migrate
python manage.py createsuperuser
```

**Follow the prompts to create your admin username and password.**

### Step 7: Start the System

```bash
python manage.py runserver 0.0.0.0:8000
```

**Keep this terminal window open - your system is now running!**

### Step 8: Access Your System

1. **Find your Pi's IP address:**

   ```bash
   hostname -I
   ```

2. **Open a web browser on any device and go to:**

   ```
   http://[YOUR_PI_IP]:8000
   ```

   Example: `http://192.168.1.100:8000`

**🎉 You should now see your irrigation control panel!**

---

## Daily Usage

### To Start the System

```bash
cd auto-irregation
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000
```

### To Stop the System

Press `Ctrl + C` in the terminal

### Access from Phone/Computer

Open browser → go to `http://[PI_IP]:8000`

---

## Web Interface Guide

### Main Dashboard

- **Current Status**: Temperature, humidity, soil moisture
- **Manual Controls**: Turn water on/off manually
- **Camera View**: Live video of your garden
- **History**: View past sensor readings

### Automatic Mode

- System waters plants when soil is dry
- All watering events are logged
- You can adjust settings from the web interface

---

## If Something Goes Wrong

### "Can't connect to database"

```bash
sudo systemctl start mysql
```

### "Permission denied"

```bash
chmod +x manage.py
sudo chown -R pi:pi /home/pi/auto-irregation
```

### "Web page won't load"

1. Make sure the terminal with the server is still running
2. Check your Pi's IP: `hostname -I`
3. Try `http://localhost:8000` on the Pi itself

### "Python version error"

```bash
python3.11 --version
```

Should show Python 3.11.x

### "Camera not working"

```bash
sudo raspi-config
```

Go to Interface Options → Camera → Enable → Reboot

### "Sensors not reading"

1. Check all wire connections against the diagram
2. Test GPIO: `python3.11 -c "import RPi.GPIO as GPIO; print('GPIO OK')"`

### Start Over (if everything breaks)

```bash
rm -rf venv
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
```

---

## Quick Reference

### Essential Commands

```bash
# Start system
cd auto-irrigation && source venv/bin/activate && python manage.py runserver 0.0.0.0:8000

# Stop system
# Press Ctrl + C

# Check database
python manage.py check

# Find Pi IP
hostname -I

# Restart MySQL
sudo systemctl restart mysql
```

### File Locations

- **Project folder**: `/home/pi/auto-irrigation/`
- **Database settings**: `config/settings.py`
- **Sensor code**: `web/soil_sensor.py`
- **Camera code**: `web/views.py`

### Default Settings

- **Database name**: `grass_database`
- **Database user**: `root`
- **Database password**: `123456`
- **Web port**: `8000`
- **Time zone**: `Asia/Shanghai`

---

## Need Help?

1. **Check if commands copied correctly** - spaces and spelling matter
2. **Make sure Pi is connected to internet**
3. **Double-check hardware wiring** against the diagram
4. **Try restarting your Pi** if nothing works
5. **Search the error message** on Google - others have likely solved it

**Remember**: Copy each command exactly as shown, press Enter, wait for it to finish, then do the next one.

**Happy Gardening!** 🌱💧

