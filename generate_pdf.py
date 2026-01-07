#!/usr/bin/env python3
# File: generate_pdf.py

"""
Generate a beautiful red-themed A4 PDF with a WiFi QR code generated from .env file.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from PIL import Image
import qrcode
from qrcode import constants as qrcode_constants
from dotenv import load_dotenv
import os
import tempfile
import time
import hashlib
import argparse
import yaml
from dataclasses import dataclass
from typing import Dict, Optional, Any, cast


@dataclass
class DesignTheme:
    """Design theme configuration"""

    name: str
    primary_color: Any  # HexColor
    secondary_color: Any  # HexColor
    accent_color: Any  # HexColor
    background_color: Any  # HexColor
    info_box_color: Any  # HexColor
    text_color: Any  # HexColor
    text_secondary: Any  # HexColor
    border_color: Any  # HexColor
    title_color: Any  # HexColor
    has_top_bar: bool = True
    has_border: bool = False
    border_width: float = 0
    corner_size: float = 0


def load_themes_from_yaml(yaml_path: str = "themes.yaml") -> Dict[str, DesignTheme]:
    """
    Load design themes from YAML configuration file.

    Args:
        yaml_path: Path to the themes YAML file

    Returns:
        Dictionary of theme keys to DesignTheme objects
    """
    if not os.path.exists(yaml_path):
        raise FileNotFoundError(f"Themes file not found: {yaml_path}")

    with open(yaml_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if "themes" not in config:
        raise ValueError("YAML file must contain a 'themes' key")

    themes = {}
    for theme_key, theme_data in config["themes"].items():
        colors = theme_data.get("colors", {})
        layout = theme_data.get("layout", {})

        theme = DesignTheme(
            name=theme_data.get("name", theme_key.title()),
            primary_color=HexColor(colors.get("primary", "#000000")),
            secondary_color=HexColor(colors.get("secondary", "#000000")),
            accent_color=HexColor(colors.get("accent", "#000000")),
            background_color=HexColor(colors.get("background", "#FFFFFF")),
            info_box_color=HexColor(colors.get("info_box", "#FFFFFF")),
            text_color=HexColor(colors.get("text", "#000000")),
            text_secondary=HexColor(colors.get("text_secondary", "#666666")),
            border_color=HexColor(colors.get("border", "#CCCCCC")),
            title_color=HexColor(colors.get("title", "#000000")),
            has_top_bar=layout.get("has_top_bar", True),
            has_border=layout.get("has_border", False),
            border_width=layout.get("border_width", 0),
            corner_size=layout.get("corner_size", 0),
        )
        themes[theme_key] = theme

    return themes


def get_design_themes(yaml_path: str = "themes.yaml") -> Dict[str, DesignTheme]:
    """
    Get available design themes from YAML file.

    Args:
        yaml_path: Path to the themes YAML file (default: themes.yaml)

    Returns:
        Dictionary of theme keys to DesignTheme objects
    """
    try:
        return load_themes_from_yaml(yaml_path)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
        print(f"Warning: Could not load themes from {yaml_path}: {e}")
        print("Falling back to default FritzBox theme...")
        # Return a minimal default theme
        return {
            "fritzbox": DesignTheme(
                name="FritzBox",
                primary_color=HexColor("#0066CC"),
                secondary_color=HexColor("#004499"),
                accent_color=HexColor("#0066CC"),
                background_color=HexColor("#FFFFFF"),
                info_box_color=HexColor("#E6F2FF"),
                text_color=HexColor("#333333"),
                text_secondary=HexColor("#666666"),
                border_color=HexColor("#CCCCCC"),
                title_color=HexColor("#FFFFFF"),
                has_top_bar=True,
                has_border=False,
            )
        }


def load_wifi_data_from_env():
    """
    Load WiFi information from environment variables (.env file).

    Returns:
        Dictionary with WiFi information (SSID, Password, Security)
    """
    load_dotenv()

    wifi_data = {
        "SSID": os.getenv("WIFI_SSID", ""),
        "Password": os.getenv("WIFI_PASSWORD", ""),
        "Security": os.getenv("WIFI_SECURITY", "WPA2"),
    }

    # Validate required fields
    if not wifi_data["SSID"]:
        raise ValueError("WIFI_SSID is required in .env file")
    if not wifi_data["Password"]:
        raise ValueError("WIFI_PASSWORD is required in .env file")

    return wifi_data


def generate_wifi_qr_code(ssid, password, security="WPA2") -> Image.Image:
    """
    Generate a WiFi QR code image from WiFi credentials.

    Args:
        ssid: Network SSID
        password: Network password
        security: Security type (WPA, WPA2, WEP, nopass)

    Returns:
        PIL Image object of the QR code
    """
    # WiFi QR code format: WIFI:T:WPA2;S:SSID;P:password;;
    # Escape special characters in SSID and password
    ssid_escaped = (
        ssid.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace(":", "\\:")
    )
    password_escaped = (
        password.replace("\\", "\\\\")
        .replace(";", "\\;")
        .replace(",", "\\,")
        .replace(":", "\\:")
    )

    wifi_string = f"WIFI:T:{security};S:{ssid_escaped};P:{password_escaped};;"

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode_constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(wifi_string)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")
    return cast(Image.Image, img)


def create_pdf(
    wifi_data,
    output_path="wifi_qr_code.pdf",
    theme: Optional[DesignTheme] = None,
    qr_size: Optional[float] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    show_footer: bool = True,
):
    """
    Create a beautiful A4 PDF with the QR code image and WiFi information.

    Args:
        wifi_data: Dictionary with WiFi information (SSID, Password, Security)
        output_path: Output PDF file path
        theme: DesignTheme object (default: FritzBox theme)
        qr_size: QR code size as fraction of page (default: 0.35)
        title: Custom title text (default: "WiFi Network Access")
        subtitle: Custom subtitle text
        show_footer: Whether to show footer text
    """
    # Get theme (default to FritzBox)
    if theme is None:
        themes = get_design_themes()
        theme = themes["fritzbox"]

    # Set defaults
    if qr_size is None:
        qr_size = 0.35
    if title is None:
        title = "WiFi Network Access"
    if subtitle is None:
        subtitle = "Scan the QR code or use the connection details below"

    # Generate QR code from WiFi data
    qr_img: Image.Image = generate_wifi_qr_code(
        wifi_data["SSID"], wifi_data["Password"], wifi_data.get("Security", "WPA2")
    )

    # Create PDF canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Use theme colors
    primary_color = theme.primary_color
    secondary_color = theme.secondary_color
    accent_color = theme.accent_color
    background_color = theme.background_color
    info_box_color = theme.info_box_color
    text_color = theme.text_color
    text_secondary = theme.text_secondary
    border_color = theme.border_color
    title_color = theme.title_color

    # Draw background
    c.setFillColor(background_color)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Draw border if theme has one
    if theme.has_border and theme.border_width > 0:
        border_w = theme.border_width * mm
        c.setFillColor(primary_color)
        c.rect(0, 0, width, border_w, fill=1, stroke=0)  # Bottom
        c.rect(0, height - border_w, width, border_w, fill=1, stroke=0)  # Top
        c.rect(0, 0, border_w, height, fill=1, stroke=0)  # Left
        c.rect(width - border_w, 0, border_w, height, fill=1, stroke=0)  # Right

        # Corner accents if specified
        if theme.corner_size > 0:
            corner_s = theme.corner_size * mm
            c.setFillColor(secondary_color)
            c.rect(0, 0, corner_s, corner_s, fill=1, stroke=0)
            c.rect(width - corner_s, 0, corner_s, corner_s, fill=1, stroke=0)
            c.rect(0, height - corner_s, corner_s, corner_s, fill=1, stroke=0)
            c.rect(
                width - corner_s,
                height - corner_s,
                corner_s,
                corner_s,
                fill=1,
                stroke=0,
            )

    # Draw top accent bar if theme has one
    accent_height = 8 * mm
    if theme.has_top_bar:
        c.setFillColor(primary_color)
        c.rect(0, height - accent_height, width, accent_height, fill=1, stroke=0)

    # Calculate QR code size
    max_qr_size = min(width * qr_size, height * qr_size)
    qr_width, qr_height = qr_img.size
    aspect_ratio = qr_width / qr_height

    if aspect_ratio > 1:
        qr_display_width = max_qr_size
        qr_display_height = max_qr_size / aspect_ratio
    else:
        qr_display_height = max_qr_size
        qr_display_width = max_qr_size * aspect_ratio

    # Position QR code - leave space for title/subtitle at top
    # Title area: accent bar (8mm) + title (30mm) + subtitle (20mm) + spacing (20mm) = ~78mm
    top_space = accent_height + 30 * mm + 25 * mm + 20 * mm if theme.has_top_bar else 30 * mm + 25 * mm + 20 * mm
    qr_x = (width - qr_display_width) / 2
    qr_y = height - top_space - qr_display_height

    # Draw subtle frame around QR code (Fritz!Box style)
    frame_padding = 15 * mm
    frame_x = qr_x - frame_padding
    frame_y = qr_y - frame_padding
    frame_width = qr_display_width + (2 * frame_padding)
    frame_height = qr_display_height + (2 * frame_padding)

    # Draw frame around QR code
    c.setFillColor(info_box_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(1)
    c.roundRect(frame_x, frame_y, frame_width, frame_height, 5 * mm, fill=1, stroke=1)

    # Save QR code to temporary file for ReportLab
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        qr_img.save(tmp_file)
        tmp_path = tmp_file.name

    try:
        # Draw QR code image
        c.drawImage(
            tmp_path, qr_x, qr_y, width=qr_display_width, height=qr_display_height
        )
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

    # Add title text (in the accent bar if it exists, otherwise below it)
    if theme.has_top_bar:
        title_y = height - accent_height + 2 * mm  # Inside the accent bar
    else:
        title_y = height - 25 * mm  # Below where accent bar would be
    c.setFillColor(title_color)
    c.setFont("Helvetica-Bold", 24)
    text_width = c.stringWidth(title, "Helvetica-Bold", 24)
    c.drawString((width - text_width) / 2, title_y - 4 * mm, title)

    # Add subtitle below title with proper spacing
    if subtitle:
        subtitle_y = title_y - 30 * mm  # Below title with spacing
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 14)
        subtitle_width = c.stringWidth(subtitle, "Helvetica", 14)
        c.drawString((width - subtitle_width) / 2, subtitle_y, subtitle)

    # Display WiFi information RIGHT BELOW the QR code
    # In ReportLab: y=0 is at bottom, y increases upward
    # qr_y is the bottom of the QR code image
    # frame_y = qr_y - frame_padding is the bottom of the frame (frame extends below QR code)
    # To place info BELOW the frame, we need to go DOWN (subtract from y)
    frame_bottom = frame_y  # Bottom of the frame
    info_start_y = frame_bottom - 30 * mm  # Below QR code frame with spacing

    # WiFi info box dimensions
    info_box_width = width * 0.75
    info_box_x = (width - info_box_width) / 2

    # Section title
    section_title_y = info_start_y
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 18)
    section_title = "Connection Details"
    section_title_width = c.stringWidth(section_title, "Helvetica-Bold", 18)
    c.drawString(info_box_x, section_title_y, section_title)

    # Draw info boxes - positioned below section title
    box_height = 20 * mm
    box_spacing = 5 * mm
    box_y = section_title_y - 25 * mm  # Below section title with spacing

    # SSID Box
    c.setFillColor(info_box_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(1)
    c.roundRect(info_box_x, box_y, info_box_width, box_height, 3 * mm, fill=1, stroke=1)

    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(info_box_x + 10 * mm, box_y + 12 * mm, "Network Name (SSID):")
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 16)
    ssid_text = wifi_data.get("SSID", "")
    c.drawString(info_box_x + 10 * mm, box_y + 2 * mm, ssid_text)

    # Security Box
    box_y -= box_height + box_spacing
    c.setFillColor(info_box_color)
    c.roundRect(info_box_x, box_y, info_box_width, box_height, 3 * mm, fill=1, stroke=1)

    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(info_box_x + 10 * mm, box_y + 12 * mm, "Security Type:")
    c.setFillColor(text_secondary)
    c.setFont("Helvetica", 14)
    security_text = wifi_data.get("Security", "WPA2")
    c.drawString(info_box_x + 10 * mm, box_y + 2 * mm, security_text)

    # Password Box
    box_y -= box_height + box_spacing
    c.setFillColor(info_box_color)
    c.roundRect(info_box_x, box_y, info_box_width, box_height, 3 * mm, fill=1, stroke=1)

    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(info_box_x + 10 * mm, box_y + 12 * mm, "Password:")
    c.setFillColor(primary_color)
    c.setFont("Courier-Bold", 15)  # Monospace for password clarity
    password_text = wifi_data.get("Password", "")
    # Adjust font size if password is too long
    max_password_width = info_box_width - 20 * mm
    if c.stringWidth(password_text, "Courier-Bold", 15) > max_password_width:
        c.setFont("Courier-Bold", 12)
    c.drawString(info_box_x + 10 * mm, box_y + 2 * mm, password_text)

    # Add footer if enabled
    if show_footer:
        bottom_y = 25 * mm
        c.setFillColor(text_secondary)
        c.setFont("Helvetica", 10)
        footer_text = "Keep this document for easy WiFi network access"
        footer_width = c.stringWidth(footer_text, "Helvetica", 10)
        c.drawString((width - footer_width) / 2, bottom_y, footer_text)

    # Save the PDF
    c.save()
    print(f"✓ PDF created successfully: {output_path}")


def parse_arguments():
    """Parse command-line arguments"""
    themes = get_design_themes()
    theme_names = ", ".join(themes.keys())

    parser = argparse.ArgumentParser(
        description="Generate WiFi QR code PDF with customizable design themes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available themes: {theme_names}

Examples:
  python generate_pdf.py --theme fritzbox
  python generate_pdf.py --theme red --qr-size 0.4
  python generate_pdf.py --theme minimal --title "My WiFi Network"
  python generate_pdf.py --theme dark --no-footer
        """,
    )

    parser.add_argument(
        "--theme",
        "-t",
        type=str,
        default="fritzbox",
        choices=list(themes.keys()),
        help=f"Design theme to use (default: fritzbox). Choices: {theme_names}",
    )

    parser.add_argument(
        "--qr-size",
        "-s",
        type=float,
        default=0.35,
        help="QR code size as fraction of page (default: 0.35, range: 0.2-0.5)",
    )

    parser.add_argument(
        "--title",
        type=str,
        default=None,
        help='Custom title text (default: "WiFi Network Access")',
    )

    parser.add_argument(
        "--subtitle", type=str, default=None, help="Custom subtitle text"
    )

    parser.add_argument("--no-footer", action="store_true", help="Hide footer text")

    parser.add_argument(
        "--list-themes", action="store_true", help="List all available themes and exit"
    )

    parser.add_argument(
        "--themes-file",
        type=str,
        default="themes.yaml",
        help="Path to themes YAML file (default: themes.yaml)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate PDFs for all available themes",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()

    # List themes and exit if requested
    if args.list_themes:
        themes = get_design_themes(args.themes_file)
        print("Available design themes:")
        print("-" * 60)
        for name, theme in themes.items():
            print(f"  {name:12} - {theme.name}")
        print("-" * 60)
        print(f"\nThemes loaded from: {args.themes_file}")
        exit(0)

    try:
        # Validate QR size
        if args.qr_size < 0.2 or args.qr_size > 0.5:
            print("Warning: QR size should be between 0.2 and 0.5. Using default 0.35")
            args.qr_size = 0.35

        # Load WiFi data from .env file
        wifi_data = load_wifi_data_from_env()
        print(f"✓ Loaded WiFi data: {wifi_data.get('SSID', 'Unknown')}")

        # Get all themes
        themes = get_design_themes(args.themes_file)
        if not themes:
            raise ValueError("No themes available. Please check themes.yaml file.")

        # Create output directory if it doesn't exist
        output_dir = "output"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"✓ Created output directory: {output_dir}")

        # Handle --all flag: generate PDFs for all themes
        if args.all:
            print(f"✓ Generating PDFs for all {len(themes)} themes...")
            print("-" * 60)
            generated_count = 0
            
            for theme_key, theme in themes.items():
                try:
                    # Generate unique hash for each PDF (timestamp + theme name)
                    nanoseconds = time.time_ns()
                    hash_input = f"{nanoseconds}{theme_key}{args.qr_size}"
                    hash_obj = hashlib.sha256(hash_input.encode())
                    hash_hex = hash_obj.hexdigest()
                    
                    # Create PDF filename with hash
                    output_pdf = os.path.join(output_dir, f"{hash_hex}.pdf")
                    
                    # Create PDF for this theme
                    create_pdf(
                        wifi_data,
                        output_pdf,
                        theme=theme,
                        qr_size=args.qr_size,
                        title=args.title,
                        subtitle=args.subtitle,
                        show_footer=not args.no_footer,
                    )
                    generated_count += 1
                    print(f"  [{generated_count}/{len(themes)}] ✓ {theme.name}")
                except Exception as e:
                    print(f"  ✗ Failed to generate PDF for {theme.name}: {e}")
            
            print("-" * 60)
            print(f"✓ Successfully generated {generated_count}/{len(themes)} PDFs")
        else:
            # Single theme mode
            if args.theme not in themes:
                print(f"Warning: Theme '{args.theme}' not found in {args.themes_file}")
                print(f"Available themes: {', '.join(themes.keys())}")
                print("Using default 'fritzbox' theme...")
                args.theme = "fritzbox"
            selected_theme = themes.get(
                args.theme, list(themes.values())[0] if themes else None
            )
            if selected_theme:
                print(f"✓ Using theme: {selected_theme.name} (from {args.themes_file})")
            else:
                raise ValueError("No themes available. Please check themes.yaml file.")

            # Generate hash from nanoseconds since 1970
            nanoseconds = time.time_ns()
            hash_obj = hashlib.sha256(str(nanoseconds).encode())
            hash_hex = hash_obj.hexdigest()

            # Create PDF filename with hash
            output_pdf = os.path.join(output_dir, f"{hash_hex}.pdf")

            # Create PDF
            create_pdf(
                wifi_data,
                output_pdf,
                theme=selected_theme,
                qr_size=args.qr_size,
                title=args.title,
                subtitle=args.subtitle,
                show_footer=not args.no_footer,
            )
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease create a .env file with the following variables:")
        print("WIFI_SSID=YourNetworkName")
        print("WIFI_PASSWORD=YourPassword")
        print("WIFI_SECURITY=WPA2")
    except Exception as e:
        print(f"An error occurred: {e}")
