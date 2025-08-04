# Raspberry Pi 4B Automated Irrigation System Setup Guide

## Table of Contents
1. [Hardware Requirements](#hardware-requirements)
2. [Raspberry Pi OS Setup](#raspberry-pi-os-setup)
3. [Hardware Connections](#hardware-connections)
4. [Software Installation](#software-installation)
5. [Database Configuration](#database-configuration)  
6. [System Configuration](#system-configuration)
7. [Starting the System](#starting-the-system)
8. [Testing and Troubleshooting](#testing-and-troubleshooting)

## 1. Hardware Requirements

### Required Components:
- **Raspberry Pi 4B** (4GB RAM recommended, 2GB minimum)
- **Official Pi 4B Power Supply** (5V 3A USB-C)
- **MicroSD Card**: 32GB Class 10 or higher (SanDisk Extreme recommended)
- **USB Camera** or **Pi Camera Module v2**
- **Soil Temperature/Humidity Sensor** with UART output
- **12V Solenoid Water Valve**
- **5V Relay Module** (compatible with Pi 4B GPIO)
- **Jumper Wires** and **Breadboard**
- **12V Power Supply** for water valve (2A minimum)
- **Ethernet Cable** or use Pi 4B built-in WiFi

### Optional Components:
- **Waterproof Enclosure** for outdoor deployment (IP65 rated)
- **Official Pi 4B Case** with cooling fan
- **MicroHDMI Cable** for Pi 4B display connection
- **LCD Display** for local status monitoring
- **LEDs** for status indication
- **Heat sinks** for Pi 4B (recommended for continuous operation)

## 2. Raspberry Pi 4B OS Setup

### 2.1 Install Raspberry Pi OS
```bash
# Use Raspberry Pi Imager to flash Raspberry Pi OS (64-bit) or Ubuntu 20.04 LTS for Pi 4B
# Recommended: Raspberry Pi OS Lite (64-bit) for better performance on Pi 4B
# Enable SSH, Camera, and Serial interfaces in raspi-config
sudo raspi-config

# Navigate to:
# - Interface Options > SSH > Enable
# - Interface Options > Camera > Enable  
# - Interface Options > Serial > Enable (but disable serial console)
```

### 2.2 Update System
```bash
sudo apt update && sudo apt upgrade -y
sudo reboot
```

### 2.3 Enable UART Serial Port (Pi 4B Specific)
```bash
# Edit boot config for Pi 4B
sudo nano /boot/config.txt

# Add these lines for Pi 4B:
enable_uart=1
dtoverlay=disable-bt
# Pi 4B specific: Ensure adequate power
over_voltage=2
arm_freq=1500

# Disable serial console
sudo systemctl stop serial-getty@ttyAMA0.service
sudo systemctl disable serial-getty@ttyAMA0.service

# Edit cmdline.txt to remove console
sudo nano /boot/cmdline.txt
# Remove: console=serial0,115200 console=ttyAMA0,115200

sudo reboot
```

## 3. Hardware Connections

**IMPORTANT:** Follow the wiring diagram below for complete component connections.

![Hardware Wiring Diagram](hardware.png)

### 3.1 Connection Overview
The hardware setup includes:
- Raspberry Pi 4B as the main controller
- Soil temperature/humidity sensor connected via UART
- 5V relay module for water valve control
- 12V solenoid water valve
- USB or Pi Camera module

All specific pin connections, GPIO assignments, and wiring details are shown in the diagram above.

### 3.2 Camera Setup (Pi 4B Specific)
```bash
# Pi 4B has 4 USB ports: 2x USB 3.0 (blue) and 2x USB 2.0 (black)
# For USB Camera: 
#   - Use USB 3.0 ports (blue) for high-resolution cameras
#   - USB 2.0 ports work fine for standard 720p/1080p cameras
#   - Pi 4B can handle multiple USB cameras simultaneously

# For Pi Camera Module v2:
#   - Connect to dedicated camera port with ribbon cable
#   - Pi 4B supports both original and HQ camera modules
#   - Hardware acceleration available for camera processing

# Pi 4B Camera Detection:
v4l2-ctl --list-devices
ls /dev/video*

# Check USB camera capabilities (Pi 4B specific):
v4l2-ctl --device=/dev/video0 --list-formats-ext

# Test camera with Pi 4B hardware acceleration:
libcamera-hello --preview  # For Pi Camera
fswebcam -r 1280x720 test.jpg  # For USB Camera
```

## 4. Software Installation

### 4.1 Install Python Dependencies (Pi 4B Optimized)
```bash
# Pi 4B supports Python 3.9+ with better performance
# Install Python 3.11 for optimal performance on Pi 4B's ARM Cortex-A72
sudo apt install python3.11 python3.11-pip python3.11-venv python3.11-dev -y

# Pi 4B specific: Install build tools for native compilation
sudo apt install build-essential cmake pkg-config -y

# Create virtual environment optimized for Pi 4B
cd /home/pi/Desktop
mkdir auto_irrigate
cd auto_irrigate
python3.11 -m venv venv --prompt="irrigation-pi4b"
source venv/bin/activate

# Pi 4B: Upgrade pip for better wheel support
pip install --upgrade pip setuptools wheel
```

### 4.2 Install System Dependencies (Pi 4B Optimized)
```bash
# Install MySQL optimized for Pi 4B's 4GB RAM
sudo apt install mysql-server mysql-client -y
sudo apt install libmysqlclient-dev -y
sudo apt install python3.11-dev -y

# Pi 4B OpenCV with hardware acceleration support
sudo apt install libopencv-dev python3-opencv -y
sudo apt install libcamera-dev libcamera-apps -y

# Pi 4B GPU acceleration libraries
sudo apt install libblas-dev liblapack-dev libatlas-base-dev -y
sudo apt install libhdf5-dev libhdf5-serial-dev -y

# Serial communication libraries
sudo apt install python3-serial -y

# Pi 4B specific system tools
sudo apt install git curl wget htop iotop -y
sudo apt install v4l-utils fswebcam -y

# Pi 4B: Install additional multimedia libraries
sudo apt install ffmpeg libavcodec-dev libavformat-dev libswscale-dev -y
sudo apt install libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev -y
```

### 4.3 Clone and Setup Project (Pi 4B Optimized)
```bash
# Clone the project repository
git clone https://github.com/nobody4t/auto-irregation.git /home/pi/Desktop/auto_irrigate

cd /home/pi/Desktop/auto_irrigate
source venv/bin/activate

# Pi 4B: Set environment variables for optimal compilation
export CFLAGS="-march=armv8-a+crc -mtune=cortex-a72"
export CXXFLAGS="$CFLAGS"

# Install Python requirements with Pi 4B optimizations
pip install -r requirements.txt

# If requirements.txt has issues, install manually with Pi 4B optimizations:
pip install django==4.2.7
pip install pymysql==1.1.1
pip install django-cors-headers==4.5.0

# Pi 4B: Install OpenCV with hardware acceleration
pip install opencv-python-headless  # Lighter version for Pi 4B

# Pi 4B GPIO library (updated for Pi 4B)
pip install RPi.GPIO
pip install gpiozero  # Modern alternative with Pi 4B optimizations

# Serial communication
pip install pyserial

# Pi 4B: Additional performance libraries
pip install numpy --no-cache-dir  # Prevent memory issues during install
pip install Pillow  # Optimized image processing

# Pi 4B: Install monitoring tools
pip install psutil  # System monitoring
```

## 5. Database Configuration

The project uses MySQL database with existing models and migrations.

### 5.1 Setup MySQL
```bash
# Secure MySQL installation
sudo mysql_secure_installation

# Create database and user
sudo mysql -u root -p

# In MySQL console:
CREATE DATABASE grass_database;
CREATE USER 'root'@'localhost' IDENTIFIED BY '123456';
GRANT ALL PRIVILEGES ON grass_database.* TO 'root'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### 5.2 Database Models
The system includes two main models:
- **GrassEnvironment**: Stores sensor data (Time, Temperature, Humidity)
- **AnimalRecord**: Stores animal detection records (Time, Record)

### 5.3 Django Database Migration
```bash
cd /home/pi/Desktop/auto_irrigate
source venv/bin/activate

# Run existing migrations (migrations already exist in the project)
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser
```

**Note:** The project already contains migration files in `web/migrations/`. No need to run `makemigrations` unless you modify the models.

## 6. System Configuration

### 6.1 Django Configuration
The Django settings are already configured in `config/settings.py`:
- Database: MySQL with `grass_database`
- Debug mode: Enabled for development
- CORS: Configured for cross-origin requests
- Static files: Located in `static/` directory
- Templates: Located in `templates/` directory

### 6.2 Important Settings
```python
# Database configuration (already set)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'grass_database',
        'USER': 'root',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}

# Time zone (already set to Shanghai)
TIME_ZONE = 'Asia/Shanghai'
USE_TZ = False
```

### 6.3 Test Hardware Connections
```bash
# Test soil sensor
cd /home/pi/Desktop/auto_irrigate
source venv/bin/activate
python web/soil_sensor.py

# Test water valve
python web/valve_control.py

# Test camera
python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera working!' if cap.read()[0] else 'Camera failed')"
```

### 6.4 Create Startup Script
```bash
# Make start.sh executable
chmod +x start.sh

# Create systemd service (optional)
sudo nano /etc/systemd/system/irrigation.service
```

Add to irrigation.service:
```ini
[Unit]
Description=Auto Irrigation System
After=network.target mysql.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Desktop/auto_irrigate
Environment=PATH=/home/pi/Desktop/auto_irrigate/venv/bin
ExecStart=/home/pi/Desktop/auto_irrigate/venv/bin/python manage.py runserver 0.0.0.0:8000
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable service:
```bash
sudo systemctl daemon-reload
sudo systemctl enable irrigation.service
```

## 7. Starting the System

### 7.1 Manual Start
```bash
cd /home/pi/Desktop/auto_irrigate
source venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Or use the start script:
./start.sh
```

### 7.2 Auto Start on Boot
```bash
# Start the systemd service
sudo systemctl start irrigation.service

# Check status
sudo systemctl status irrigation.service
```

### 7.3 Access Web Interface
```
# Open browser and navigate to:
http://[PI_IP_ADDRESS]:8000

# Example:
http://192.168.1.100:8000
```

## 8. Testing and Troubleshooting

### 8.1 System Tests
```bash
# Test sensor data collection
curl http://localhost:8000/getsensordata/

# Test valve control
curl -X POST http://localhost:8000/valvecontrol/ \
  -H "Content-Type: application/json" \
  -d '{"content": {"operate": "open"}}'

# Test camera stream
curl http://localhost:8000/video_stream/
```

### 8.2 Common Issues

**1. Serial Port Permission Denied**
```bash
sudo usermod -a -G dialout pi
sudo reboot
```

**2. GPIO Permission Issues**  
```bash
sudo usermod -a -G gpio pi
# Or run with sudo (not recommended for production)
```

**3. Camera Not Detected**
```bash
# For USB camera
sudo apt install v4l-utils
v4l2-ctl --list-devices

# For Pi camera
sudo raspi-config
# Enable camera interface
```

**4. MySQL Connection Issues**
```bash
# Check MySQL status
sudo systemctl status mysql

# Reset MySQL password
sudo mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY '123456';
```

**5. Django Static Files**
```bash
python manage.py collectstatic
```

### 8.3 Log Files
```bash
# System logs
sudo journalctl -u irrigation.service -f

# Django debug output
tail -f /var/log/django.log  # if configured

# MySQL logs
sudo tail -f /var/log/mysql/error.log
```

### 8.4 Performance Optimization (Pi 4B Specific)
```bash
# Pi 4B Boot Configuration Optimizations
sudo nano /boot/config.txt

# Add these Pi 4B specific optimizations:
# GPU memory for camera and video processing
gpu_mem=256

# Pi 4B CPU performance settings
arm_freq=1800          # Overclock to 1.8GHz (safe with cooling)
over_voltage=2         # Slight overvoltage for stability
temp_limit=75          # Temperature limit

# Pi 4B specific USB optimizations
dwc_otg.speed=1        # USB optimizations

# Enable hardware acceleration
dtoverlay=vc4-kms-v3d
max_framebuffers=2

# Pi 4B MySQL Optimization for 4GB RAM
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Add under [mysqld] for Pi 4B:
innodb_buffer_pool_size = 512M    # Use more RAM on Pi 4B
max_connections = 100             # Pi 4B can handle more connections
innodb_log_file_size = 64M
query_cache_size = 64M
query_cache_limit = 2M
tmp_table_size = 32M
max_heap_table_size = 32M

# Pi 4B System-wide optimizations
sudo nano /etc/sysctl.conf

# Add these lines for Pi 4B networking:
net.core.rmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_default = 262144
net.core.wmem_max = 16777216

# Pi 4B Swap optimization (with 4GB RAM)
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# Set: CONF_SWAPSIZE=2048  # 2GB swap for Pi 4B
sudo dphys-swapfile setup
sudo dphys-swapfile swapon

# Pi 4B: Enable zram for better memory management
sudo apt install zram-tools -y
echo 'ALGO=lz4' | sudo tee -a /etc/default/zramswap
echo 'PERCENT=25' | sudo tee -a /etc/default/zramswap
sudo systemctl enable zramswap

# Apply changes
sudo reboot
```

## 9. Security Considerations

### 9.1 Production Security
```bash
# Change default database password
# Disable DEBUG mode in settings.py
# Configure proper ALLOWED_HOSTS
# Enable CSRF protection
# Use environment variables for secrets
```


## 10. Maintenance

### 10.1 Regular Tasks
- Check sensor calibration monthly
- Clean camera lens weekly  
- Verify valve operation weekly
- Backup database monthly
- Update system packages monthly

### 10.2 Data Export
The system provides automatic TXT report generation through the web interface at `/generaltxt/` endpoint.

---

## Quick Start Summary (Raspberry Pi 4B)
1. Flash **Raspberry Pi OS (64-bit)** to SD card (32GB+ Class 10)
2. Enable SSH, Camera, Serial in raspi-config on **Pi 4B**
3. Install Pi 4B optimized dependencies: `sudo apt install mysql-server libmysqlclient-dev python3.11-dev libopencv-dev libcamera-dev`
4. Setup database: Create `grass_database` with Pi 4B MySQL optimizations
5. Install Python packages with Pi 4B optimizations: `pip install -r requirements.txt`
6. Run migrations: `python manage.py migrate`
7. Connect hardware using **Pi 4B GPIO pinout** and utilize **4 USB ports** (2x USB 3.0, 2x USB 2.0)
8. Configure **Pi 4B boot optimizations**: `gpu_mem=256`, CPU overclock to 1.8GHz
9. Start system: `./start.sh`
10. Access web interface: `http://[PI_4B_IP]:8000`

**Pi 4B Advantages:**
- 4GB RAM enables better MySQL performance and multiple camera support
- USB 3.0 ports for high-resolution cameras
- Better processing power for real-time image analysis
- Hardware acceleration for camera and video processing
- Stable power delivery for multiple sensors

For support, check the log files and ensure all hardware connections utilize Pi 4B's enhanced capabilities.