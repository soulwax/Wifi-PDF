#!/usr/bin/env python3
# File: src/main.py

"""
WiFi QR Code PDF Generator
A standalone application for generating beautiful WiFi QR code PDFs.
"""

import argparse
import hashlib
import os
import sys
import tempfile
import time
import traceback
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Any, Dict, Optional, cast

import qrcode
import yaml
from dotenv import load_dotenv
from PIL import Image
from qrcode import constants as qrcode_constants
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent


def get_config_path(filename: str) -> Path:
    """Get path to a config file in the project root."""
    return get_project_root() / filename


@dataclass
class DesignTheme:  # pylint: disable=too-many-instance-attributes
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


def load_themes_from_yaml(yaml_path: Optional[str] = None) -> Dict[str, DesignTheme]:
    """
    Load design themes from YAML configuration file.

    Args:
        yaml_path: Path to the themes YAML file (default: themes.yaml in project root)

    Returns:
        Dictionary of theme keys to DesignTheme objects
    """
    if yaml_path is None:
        yaml_path = str(get_config_path("themes.yaml"))
    else:
        # If relative path, resolve from project root
        yaml_path = str(get_config_path(yaml_path)) if not os.path.isabs(yaml_path) else yaml_path

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


def get_design_themes(yaml_path: Optional[str] = None) -> Dict[str, DesignTheme]:
    """
    Get available design themes from YAML file.

    Args:
        yaml_path: Path to the themes YAML file (default: themes.yaml in project root)

    Returns:
        Dictionary of theme keys to DesignTheme objects
    """
    try:
        return load_themes_from_yaml(yaml_path)
    except (FileNotFoundError, ValueError, yaml.YAMLError) as e:
        print(f"Warning: Could not load themes from {yaml_path or 'themes.yaml'}: {e}")
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


def load_wifi_data_from_env(env_path: Optional[str] = None) -> Dict[str, str]:
    """
    Load WiFi information from environment variables (.env file).

    Args:
        env_path: Path to .env file (default: .env in project root)

    Returns:
        Dictionary with WiFi information (SSID, Password, Security)
    """
    if env_path is None:
        env_path = str(get_config_path(".env"))
    else:
        env_path = str(get_config_path(env_path)) if not os.path.isabs(env_path) else env_path

    load_dotenv(env_path)

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


def load_logo_image(logo_path: str) -> Image.Image:
    """
    Load logo image from file, supporting PNG, JPG, and SVG formats.

    Args:
        logo_path: Path to logo image file

    Returns:
        PIL Image object of the logo
    """
    if not os.path.exists(logo_path):
        raise FileNotFoundError(f"Logo file not found: {logo_path}")

    file_ext = os.path.splitext(logo_path)[1].lower()

    # Handle SVG files
    if file_ext == ".svg":
        try:
            from cairosvg import svg2png  # type: ignore[import-untyped]

            # Convert SVG to PNG
            png_data = svg2png(url=logo_path)
            img = Image.open(BytesIO(png_data))
            return img.convert("RGBA")
        except ImportError:
            raise ImportError(
                "SVG support requires cairosvg. Install with: pip install cairosvg"
            ) from None
        except Exception as e:
            raise ValueError(f"Failed to load SVG logo: {e}") from e

    # Handle PNG and JPG files
    try:
        img = Image.open(logo_path)
        # Convert to RGBA if needed for transparency support
        if img.mode != "RGBA":
            img = img.convert("RGBA")
        return img
    except Exception as e:
        raise ValueError(f"Failed to load logo image: {e}") from e


def generate_wifi_qr_code(
    ssid: str, password: str, security: str = "WPA2", logo_path: Optional[str] = None
) -> Image.Image:
    """
    Generate a WiFi QR code image from WiFi credentials, optionally with a logo.

    Args:
        ssid: Network SSID
        password: Network password
        security: Security type (WPA, WPA2, WEP, nopass)
        logo_path: Optional path to logo image (PNG, JPG, or SVG)

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

    # Use higher error correction if logo is present (allows logo to cover part of QR code)
    error_correction = (
        qrcode_constants.ERROR_CORRECT_H if logo_path else qrcode_constants.ERROR_CORRECT_M
    )

    # Create QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=error_correction,
        box_size=10,
        border=4,
    )
    qr.add_data(wifi_string)
    qr.make(fit=True)

    # Create image
    qr_image = qr.make_image(fill_color="black", back_color="white")
    img = cast(Image.Image, qr_image).convert("RGBA")

    # Embed logo in center if provided
    if logo_path:
        try:
            logo = load_logo_image(logo_path)

            # Calculate logo size (about 30% of QR code size, but ensure it's not too large)
            qr_width, qr_height = img.size
            logo_size = min(qr_width, qr_height) // 3  # 1/3 of QR code size

            # Resize logo maintaining aspect ratio
            logo.thumbnail((logo_size, logo_size), Image.Resampling.LANCZOS)

            # Create a white background for logo (helps with QR code readability)
            logo_bg = Image.new("RGBA", (logo_size + 20, logo_size + 20), (255, 255, 255, 255))
            logo_x = (logo_bg.width - logo.width) // 2
            logo_y = (logo_bg.height - logo.height) // 2
            logo_bg.paste(logo, (logo_x, logo_y), logo)

            # Calculate position to center logo in QR code
            qr_center_x = qr_width // 2
            qr_center_y = qr_height // 2
            paste_x = qr_center_x - logo_bg.width // 2
            paste_y = qr_center_y - logo_bg.height // 2

            # Paste logo onto QR code
            img.paste(logo_bg, (paste_x, paste_y), logo_bg)

        except Exception as e:
            print(f"Warning: Could not embed logo: {e}")
            print("Generating QR code without logo...")

    return cast(Image.Image, img.convert("RGB"))


def create_pdf(  # pylint: disable=too-many-arguments,too-many-locals,too-many-branches,too-many-statements
    wifi_data: Dict[str, str],
    output_path: str,
    *,
    theme: Optional[DesignTheme] = None,
    qr_size: Optional[float] = None,
    title: Optional[str] = None,
    subtitle: Optional[str] = None,
    show_footer: bool = True,
    logo_path: Optional[str] = None,
) -> None:
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
        wifi_data["SSID"],
        wifi_data["Password"],
        wifi_data.get("Security", "WPA2"),
        logo_path=logo_path,
    )

    # Create PDF canvas
    c = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    # Use theme colors
    primary_color = theme.primary_color
    secondary_color = theme.secondary_color
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

    # Position QR code - compact spacing for title/subtitle at top
    # Title area: accent bar (8mm) + title spacing (15mm) + title (18mm)
    # + subtitle (12mm) + spacing (8mm) = ~61mm
    if theme.has_top_bar:
        top_space = accent_height + 15 * mm + 18 * mm + 12 * mm + 8 * mm
    else:
        top_space = 18 * mm + 12 * mm + 8 * mm
    qr_x = (width - qr_display_width) / 2
    qr_y = height - top_space - qr_display_height

    # Draw subtle frame around QR code (Fritz!Box style) - more compact
    frame_padding = 10 * mm
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

    # Add title text - positioned below the accent bar to avoid overlap
    if theme.has_top_bar:
        # Below the accent bar with more spacing (lowered by 10mm)
        title_y = height - accent_height - 15 * mm
        # Use dark text color since it's on white background now
        title_text_color = text_color
    else:
        title_y = height - 20 * mm  # Below where accent bar would be
        title_text_color = title_color
    c.setFillColor(title_text_color)
    c.setFont("Helvetica-Bold", 20)
    text_width = c.stringWidth(title, "Helvetica-Bold", 20)
    c.drawString((width - text_width) / 2, title_y, title)

    # Add subtitle below title - constrain to QR code frame width
    if subtitle:
        subtitle_y = title_y - 18 * mm  # Below title with spacing
        c.setFillColor(text_secondary)
        # Use smaller font and constrain to frame width
        subtitle_font_size = 11
        c.setFont("Helvetica", subtitle_font_size)
        max_subtitle_width = frame_width - 20 * mm  # Leave margins within frame
        subtitle_width = c.stringWidth(subtitle, "Helvetica", subtitle_font_size)

        # If subtitle is too wide, reduce font size
        if subtitle_width > max_subtitle_width:
            subtitle_font_size = 14
            c.setFont("Helvetica", subtitle_font_size)
            subtitle_width = c.stringWidth(subtitle, "Helvetica", subtitle_font_size)
            if subtitle_width > max_subtitle_width:
                subtitle_font_size = 9
                c.setFont("Helvetica", subtitle_font_size)
                subtitle_width = c.stringWidth(subtitle, "Helvetica", subtitle_font_size)

        # Center subtitle (centered on page, but constrained to frame width)
        subtitle_x = (width - subtitle_width) / 2
        c.drawString(subtitle_x, subtitle_y, subtitle)

    # Display WiFi information RIGHT BELOW the QR code
    # In ReportLab: y=0 is at bottom, y increases upward
    # frame_y is the bottom of the frame (frame extends below QR code)
    # To place info BELOW the frame, we need to go DOWN (subtract from y)
    frame_bottom = frame_y  # Bottom of the frame
    info_start_y = frame_bottom - 25 * mm  # Below QR code frame with more spacing

    # WiFi info box dimensions
    info_box_width = width * 0.75
    info_box_x = (width - info_box_width) / 2

    # Section title - centered and with proper spacing
    section_title_y = info_start_y
    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 16)
    section_title = "Connection Details"
    section_title_width = c.stringWidth(section_title, "Helvetica-Bold", 16)
    # Center the section title
    section_title_x = (width - section_title_width) / 2
    c.drawString(section_title_x, section_title_y, section_title)

    # Draw info boxes - positioned below section title with more spacing
    box_height = 18 * mm
    box_spacing = 4 * mm
    box_y = section_title_y - 25 * mm  # Below section title with more spacing

    # SSID Box
    c.setFillColor(info_box_color)
    c.setStrokeColor(border_color)
    c.setLineWidth(1)
    c.roundRect(info_box_x, box_y, info_box_width, box_height, 3 * mm, fill=1, stroke=1)

    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(info_box_x + 8 * mm, box_y + 11 * mm, "Network Name (SSID):")
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 14)
    ssid_text = wifi_data.get("SSID", "")
    c.drawString(info_box_x + 8 * mm, box_y + 2 * mm, ssid_text)

    # Security Box
    box_y -= box_height + box_spacing
    c.setFillColor(info_box_color)
    c.roundRect(info_box_x, box_y, info_box_width, box_height, 3 * mm, fill=1, stroke=1)

    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(info_box_x + 8 * mm, box_y + 11 * mm, "Security Type:")
    c.setFillColor(text_secondary)
    c.setFont("Helvetica", 13)
    security_text = wifi_data.get("Security", "WPA2")
    c.drawString(info_box_x + 8 * mm, box_y + 2 * mm, security_text)

    # Password Box
    box_y -= box_height + box_spacing
    c.setFillColor(info_box_color)
    c.roundRect(info_box_x, box_y, info_box_width, box_height, 3 * mm, fill=1, stroke=1)

    c.setFillColor(text_color)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(info_box_x + 8 * mm, box_y + 11 * mm, "Password:")
    c.setFillColor(primary_color)
    c.setFont("Courier-Bold", 13)  # Monospace for password clarity
    password_text = wifi_data.get("Password", "")
    # Adjust font size if password is too long
    max_password_width = info_box_width - 16 * mm
    if c.stringWidth(password_text, "Courier-Bold", 13) > max_password_width:
        c.setFont("Courier-Bold", 11)
    c.drawString(info_box_x + 8 * mm, box_y + 2 * mm, password_text)

    # Calculate bottom of password box to ensure footer doesn't overlap
    password_box_bottom = box_y

    # Add footer if enabled - ensure it doesn't overlap with password box
    if show_footer:
        # Place footer below password box with more spacing, or at minimum 20mm from bottom
        footer_y = min(password_box_bottom - 18 * mm, 20 * mm)
        if footer_y < 15 * mm:  # If too close to bottom, skip footer
            footer_y = None

        if footer_y:
            c.setFillColor(text_secondary)
            c.setFont("Helvetica", 9)
            footer_text = "Keep this document for easy WiFi network access"
            footer_width = c.stringWidth(footer_text, "Helvetica", 9)
            c.drawString((width - footer_width) / 2, footer_y, footer_text)

    # Save the PDF
    c.save()
    print(f"✓ PDF created successfully: {output_path}")


def parse_arguments() -> argparse.Namespace:
    """Parse command-line arguments"""
    # Load themes to get available choices
    try:
        themes = get_design_themes()
        theme_names = ", ".join(themes.keys())
    except (FileNotFoundError, ValueError, yaml.YAMLError):
        themes = {}
        theme_names = "fritzbox, red, minimal, corporate, green, purple, dark"

    parser = argparse.ArgumentParser(
        description="WiFi QR Code PDF Generator - Generate beautiful WiFi QR code PDFs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Available themes: {theme_names}

Examples:
  python -m src.main --theme fritzbox
  python -m src.main --theme red --qr-size 0.4
  python -m src.main --theme minimal --title "My WiFi Network"
  python -m src.main --theme dark --no-footer
  python -m src.main --all
        """,
    )

    parser.add_argument(
        "--theme",
        "-t",
        type=str,
        default="fritzbox",
        choices=list(themes.keys()) if themes else None,
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
        default=None,
        help="Path to themes YAML file (default: themes.yaml in project root)",
    )

    parser.add_argument(
        "--all",
        action="store_true",
        help="Generate PDFs for all available themes",
    )

    parser.add_argument(
        "--logo",
        type=str,
        default=None,
        help="Path to logo image to embed in QR code center (PNG, JPG, or SVG)",
    )

    return parser.parse_args()


def main() -> int:  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
    """Main application entry point."""
    args = parse_arguments()

    # List themes and exit if requested
    if args.list_themes:
        themes = get_design_themes(args.themes_file)
        print("Available design themes:")
        print("-" * 60)
        for name, theme in themes.items():
            print(f"  {name:12} - {theme.name}")
        print("-" * 60)
        themes_file = args.themes_file or "themes.yaml"
        print(f"\nThemes loaded from: {themes_file}")
        return 0

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

        # Create output directory if it doesn't exist (in project root)
        output_dir = get_project_root() / "output"
        if not output_dir.exists():
            output_dir.mkdir()
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
                    output_pdf = output_dir / f"{hash_hex}.pdf"

                    # Create PDF for this theme
                    create_pdf(
                        wifi_data,
                        str(output_pdf),
                        theme=theme,
                        qr_size=args.qr_size,
                        title=args.title,
                        subtitle=args.subtitle,
                        show_footer=not args.no_footer,
                        logo_path=args.logo,
                    )
                    generated_count += 1
                    print(f"  [{generated_count}/{len(themes)}] ✓ {theme.name}")
                except (ValueError, OSError, IOError) as e:
                    print(f"  ✗ Failed to generate PDF for {theme.name}: {e}")

            print("-" * 60)
            print(f"✓ Successfully generated {generated_count}/{len(themes)} PDFs")
        else:
            # Single theme mode
            if args.theme not in themes:
                print(f"Warning: Theme '{args.theme}' not found")
                print(f"Available themes: {', '.join(themes.keys())}")
                print("Using default 'fritzbox' theme...")
                args.theme = "fritzbox"
            selected_theme = themes.get(
                args.theme, list(themes.values())[0] if themes else None
            )
            if selected_theme:
                themes_file = args.themes_file or "themes.yaml"
                print(f"✓ Using theme: {selected_theme.name} (from {themes_file})")
            else:
                raise ValueError("No themes available. Please check themes.yaml file.")

            # Generate hash from nanoseconds since 1970
            nanoseconds = time.time_ns()
            hash_obj = hashlib.sha256(str(nanoseconds).encode())
            hash_hex = hash_obj.hexdigest()

            # Create PDF filename with hash
            output_pdf = output_dir / f"{hash_hex}.pdf"

            # Create PDF
            create_pdf(
                wifi_data,
                str(output_pdf),
                theme=selected_theme,
                qr_size=args.qr_size,
                title=args.title,
                subtitle=args.subtitle,
                show_footer=not args.no_footer,
                logo_path=args.logo,
            )
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        print("\nPlease create a .env file in the project root with the following variables:")
        print("WIFI_SSID=YourNetworkName")
        print("WIFI_PASSWORD=YourPassword")
        print("WIFI_SECURITY=WPA2")
        return 1
    except (OSError, IOError, yaml.YAMLError) as e:
        print(f"An error occurred: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
