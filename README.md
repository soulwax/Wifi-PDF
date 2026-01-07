# WiFi QR Code PDF Generator

A Python program that generates beautifully designed A4 PDFs with WiFi QR codes and connection details. Perfect for creating printable WiFi access cards for guests, offices, or events.

## Features

- 🎨 **7+ Professional Design Themes** - Choose from FritzBox, Red, Minimal, Corporate, Green, Purple, and Dark themes
- 📱 **QR Code Generation** - Creates WiFi QR codes from scratch (no image files needed)
- 🎯 **Fully Customizable** - Adjust QR size, titles, subtitles, and more via command-line arguments
- 📋 **Connection Details** - Automatically displays SSID, password, and security type for manual entry
- 📄 **A4 Format** - Optimized for printing and standard paper sizes
- 🔒 **Secure Configuration** - Uses `.env` file to keep credentials out of code
- 🗂️ **Auto-naming** - PDFs saved with hash-based filenames in `output/` folder

## Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Design Themes](#design-themes)
- [Command-Line Options](#command-line-options)
- [Examples](#examples)
- [Output](#output)
- [Requirements](#requirements)
- [Troubleshooting](#troubleshooting)

## Quick Start

1. **Clone or download this repository**
2. **Set up virtual environment** (recommended)
3. **Install dependencies**
4. **Create `.env` file** with your WiFi credentials
5. **Run the program**

See [Installation](#installation) for detailed steps.

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Step-by-Step Installation

#### 1. Set up Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

#### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:

- `reportlab` - PDF generation
- `Pillow` - Image processing
- `qrcode` - QR code generation
- `python-dotenv` - Environment variable management

#### 3. Verify Installation

```bash
python generate_pdf.py --help
```

You should see the help message with all available options.

## Configuration

### Environment Variables

Create a `.env` file in the project root directory with your WiFi credentials:

```env
WIFI_SSID=YourNetworkName
WIFI_PASSWORD=YourPassword
WIFI_SECURITY=WPA2
```

**Important Security Notes:**

- ⚠️ Never commit `.env` files to version control
- ✅ The `.env` file is already included in `.gitignore`
- 🔒 Keep your WiFi credentials secure

### Environment Variable Reference

| Variable | Required | Description | Example Values |
|----------|----------|-------------|----------------|
| `WIFI_SSID` | **Yes** | Network name (SSID) | `MyWiFiNetwork`, `Office-Guest` |
| `WIFI_PASSWORD` | **Yes** | Network password | `MySecurePassword123` |
| `WIFI_SECURITY` | No | Security type (default: `WPA2`) | `WPA2`, `WPA`, `WEP`, `nopass` |

### Example `.env` File

```env
WIFI_SSID=Vodafone-Homenet
WIFI_PASSWORD=VonIsmael7191224!
WIFI_SECURITY=WPA2
```

## Usage

### Basic Usage

The simplest way to generate a PDF:

```bash
python generate_pdf.py
```

This will:

- Use the default **FritzBox** theme
- Generate a QR code from your `.env` credentials
- Create a PDF in the `output/` folder with a hash-based filename
- Display SSID, password, and security type on the PDF

### With Design Theme

```bash
# Red theme
python generate_pdf.py --theme red

# Minimal theme
python generate_pdf.py --theme minimal

# Dark mode theme
python generate_pdf.py --theme dark
```

### Customization

```bash
# Larger QR code with custom title
python generate_pdf.py --theme corporate --qr-size 0.4 --title "Guest WiFi Access"

# Custom subtitle and no footer
python generate_pdf.py --theme green --subtitle "Scan to connect instantly" --no-footer

# Minimal theme with all customizations
python generate_pdf.py -t minimal -s 0.3 --title "Company WiFi" --subtitle "For employees only"
```

### List Available Themes

```bash
python generate_pdf.py --list-themes
```

Output:

```
Available design themes:
--------------------------------------------------
  fritzbox    - FritzBox
  red         - Red
  minimal     - Minimal
  corporate   - Corporate
  green       - Green
  purple      - Purple
  dark        - Dark
--------------------------------------------------
```

## Design Themes

Choose a theme that matches your style or brand:

| Theme | Key | Description | Best For |
| :-----: | :-----: | :-----: | :-----: |
| **FritzBox** | `fritzbox` | Professional blue theme with clean, modern design (default) | Professional settings, offices |
| **Red** | `red` | Bold red theme with decorative borders and corner accents | Events, attention-grabbing |
| **Minimal** | `minimal` | Clean, minimal design with subtle colors | Modern, minimalist environments |
| **Corporate** | `corporate` | Professional corporate blue theme | Business, formal settings |
| **Green** | `green` | Fresh green theme with nature-inspired colors | Eco-friendly, natural settings |
| **Purple** | `purple` | Elegant purple theme | Creative, artistic environments |
| **Dark** | `dark` | Dark mode theme with light text on dark background | Modern tech, dark aesthetics |

### Theme Preview

Each theme includes:

- Unique color scheme
- Matching info boxes
- Consistent typography
- Professional layout

## Command-Line Options

### Full Command Reference

```bash
python generate_pdf.py [OPTIONS]
```

### Options

| Option | Short | Type | Default | Description |
| :-----: | :-----: | :-----: | :-----: | :-----: |
| `--theme` | `-t` | string | `fritzbox` | Design theme to use |
| `--qr-size` | `-s` | float | `0.35` | QR code size (0.2-0.5) |
| `--title` | - | string | `"WiFi Network Access"` | Custom title text |
| `--subtitle` | - | string | Auto-generated | Custom subtitle text |
| `--no-footer` | - | flag | Footer shown | Hide footer text |
| `--list-themes` | - | flag | - | List all available themes |
| `--themes-file` | - | string | `themes.yaml` | Path to themes YAML file |

### Option Details

#### `--theme` / `-t`

Select the design theme. Available themes: `fritzbox`, `red`, `minimal`, `corporate`, `green`, `purple`, `dark`

#### `--qr-size` / `-s`

Control the QR code size as a fraction of the page:

- **0.2** - Small (more space for text)
- **0.35** - Default (balanced)
- **0.5** - Large (maximum size)

**Note:** Values outside 0.2-0.5 will be automatically adjusted to the default.

#### `--title`

Custom title text displayed at the top of the PDF. Use quotes for multi-word titles:

```bash
--title "Guest WiFi Network"
```

#### `--subtitle`

Custom subtitle text displayed below the title. Use quotes for multi-word subtitles:

```bash
--subtitle "Scan QR code or enter credentials manually"
```

#### `--no-footer`

Hide the footer text at the bottom of the PDF. Useful for cleaner designs.

#### `--list-themes`

Display all available themes and exit. Useful for discovering theme names.

## Examples

### Example 1: Default Usage

```bash
python generate_pdf.py
```

- Theme: FritzBox (default)
- QR Size: 0.35 (default)
- Title: "WiFi Network Access" (default)

### Example 2: Event WiFi Card

```bash
python generate_pdf.py --theme red --title "Event WiFi" --subtitle "Free WiFi for all attendees"
```

- Bold red theme for visibility
- Custom event branding
- Clear instructions

### Example 3: Corporate Guest WiFi

```bash
python generate_pdf.py -t corporate -s 0.4 --title "Guest Network Access" --no-footer
```

- Professional corporate theme
- Larger QR code for easy scanning
- Clean design without footer

### Example 4: Minimal Office WiFi

```bash
python generate_pdf.py --theme minimal --qr-size 0.3 --title "Office WiFi"
```

- Clean, minimal design
- Smaller QR code
- Simple, professional look

### Example 5: Dark Theme for Tech Company

```bash
python generate_pdf.py --theme dark --title "Company WiFi" --subtitle "Scan to connect"
```

- Modern dark mode theme
- Tech-friendly aesthetic
- Custom branding

### Example 6: Short Form Options

```bash
# Using short flags
python generate_pdf.py -t green -s 0.4

# Mixing short and long flags
python generate_pdf.py -t purple --title "My Network"
```

## Output

### Output Location

All PDFs are saved in the `output/` directory. The directory is created automatically if it doesn't exist.

### File Naming

PDFs are named using a SHA256 hash of the creation timestamp (nanoseconds since 1970), ensuring:

- ✅ Unique filenames for each generation
- ✅ No filename conflicts
- ✅ Traceable creation time

**Example filename:**

```
output/a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456.pdf
```

### Output Structure

```
project/
├── output/
│   ├── <hash1>.pdf
│   ├── <hash2>.pdf
│   └── <hash3>.pdf
├── generate_pdf.py
├── .env
└── README.md
```

### PDF Contents

Each generated PDF includes:

1. **Title** - Customizable title at the top
2. **Subtitle** - Instructions or description
3. **QR Code** - Scannable WiFi QR code
4. **Connection Details** - Three information boxes:
   - Network Name (SSID)
   - Security Type
   - Password
5. **Footer** - Optional footer text (can be hidden)

## Requirements

### Python Version

- **Python 3.7+** (tested with Python 3.7, 3.8, 3.9, 3.10, 3.11, 3.12)

### Python Packages

All dependencies are listed in `requirements.txt`:

```
reportlab>=4.0.0
Pillow>=10.0.0
qrcode>=7.4.2
python-dotenv>=1.0.0
```

### System Requirements

- Operating System: Windows, macOS, or Linux
- Disk Space: ~10 MB for dependencies
- Memory: Minimal (suitable for all systems)

## Troubleshooting

### Common Issues

#### Issue: "WIFI_SSID is required in .env file"

**Solution:** Ensure your `.env` file exists in the project root and contains `WIFI_SSID` and `WIFI_PASSWORD` variables.

#### Issue: "ModuleNotFoundError: No module named 'reportlab'"

**Solution:** Install dependencies:

```bash
pip install -r requirements.txt
```

#### Issue: "QR size should be between 0.2 and 0.5"

**Solution:** The program will automatically use the default (0.35) if your value is out of range. Use values between 0.2 and 0.5.

#### Issue: PDF not generated

**Solution:**

1. Check that the `output/` directory is writable
2. Verify your `.env` file has correct credentials
3. Check for error messages in the console

#### Issue: QR code not scanning

**Solution:**

1. Ensure WiFi credentials in `.env` are correct
2. Try increasing QR code size: `--qr-size 0.4`
3. Verify security type matches your network

### Getting Help

1. **Check the help message:**

   ```bash
   python generate_pdf.py --help
   ```

2. **List available themes:**

   ```bash
   python generate_pdf.py --list-themes
   ```

3. **Verify your `.env` file:**
   - File exists in project root
   - Contains `WIFI_SSID` and `WIFI_PASSWORD`
   - No extra spaces or quotes around values

4. **Test with default settings:**

   ```bash
   python generate_pdf.py
   ```

## Customizing Themes

All design themes are defined in `themes.yaml`. You can:

- **Modify existing themes** - Edit colors, layout options, etc.
- **Add new themes** - Create your own custom design themes
- **Use custom themes file** - Specify a different YAML file with `--themes-file`

### Themes YAML Structure

```yaml
themes:
  theme_name:
    name: "Display Name"
    description: "Theme description"
    colors:
      primary: "#0066CC"
      secondary: "#004499"
      accent: "#0066CC"
      background: "#FFFFFF"
      info_box: "#E6F2FF"
      text: "#333333"
      text_secondary: "#666666"
      border: "#CCCCCC"
      title: "#FFFFFF"
    layout:
      has_top_bar: true
      has_border: false
      border_width: 0
      corner_size: 0
```

### Adding a New Theme

1. Open `themes.yaml`
2. Add a new theme entry following the structure above
3. Use the theme: `python generate_pdf.py --theme your_theme_name`

### Using a Custom Themes File

```bash
python generate_pdf.py --theme mytheme --themes-file custom-themes.yaml
```

## Project Structure

```
pywifipdf/
├── generate_pdf.py      # Main program
├── themes.yaml          # Design theme configurations
├── requirements.txt     # Python dependencies
├── README.md           # This file
├── .env                # WiFi credentials (create this)
├── .gitignore         # Git ignore rules
└── output/            # Generated PDFs (auto-created)
```

## License

This project is open source. Feel free to use, modify, and distribute as needed.

## Contributing

Suggestions and improvements are welcome! Some ideas:

- New design themes
- Additional customization options
- Layout variations
- Language support

---

**Enjoy generating beautiful WiFi QR code PDFs!** 🎉
