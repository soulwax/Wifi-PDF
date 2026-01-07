# WiFi QR Code PDF Generator

A Python program that creates beautiful red-themed A4 PDFs with WiFi QR codes generated from `.env` configuration.

## Quick Start

### 1. Set up Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure WiFi Settings

Create a `.env` file in the project directory with your WiFi credentials:

```env
WIFI_SSID=YourNetworkName
WIFI_PASSWORD=YourPassword
WIFI_SECURITY=WPA2
```

**Note:** Add `.env` to your `.gitignore` to keep your credentials secure!

### 4. Run the Program

```bash
python generate_pdf.py
```

The program will:
- Read WiFi credentials from `.env` file
- Generate a QR code from scratch
- Create a beautiful red-themed A4 PDF named `wifi_qr_code.pdf`

## Environment Variables

| Variable | Required | Description | Example |
|----------|----------|-------------|---------|
| `WIFI_SSID` | Yes | Network name | `MyWiFiNetwork` |
| `WIFI_PASSWORD` | Yes | Network password | `MySecurePassword123` |
| `WIFI_SECURITY` | No | Security type (default: WPA2) | `WPA2`, `WPA`, `WEP`, `nopass` |

## Features

- **QR Code Generation** - Creates WiFi QR codes from scratch (no image files needed)
- **Beautiful Red Theme** - Elegant design with decorative borders and frames
- **Connection Details** - Displays SSID, password, and security type for manual entry
- **A4 Format** - Optimized for printing
- **Secure Configuration** - Uses `.env` file to keep credentials out of code

## Requirements

- Python 3.7+
- reportlab
- Pillow
- qrcode
- python-dotenv