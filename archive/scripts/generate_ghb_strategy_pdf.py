"""
Generate PDF version of GHB Strategy Guide
Converts GHB_STRATEGY_GUIDE.md to a formatted PDF document
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    PageBreak,
    Table,
    TableStyle,
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.lib import colors
from datetime import datetime
import re


def create_ghb_strategy_pdf():
    """Generate PDF from GHB Strategy markdown guide"""

    # Read markdown file
    with open("docs/STRATEGY_D_GUIDE.md", "r", encoding="utf-8") as f:
        content = f.read()

    # Setup PDF
    output_file = f'docs/STRATEGY_D_GUIDE_{datetime.now().strftime("%Y%m%d")}.pdf'
    doc = SimpleDocTemplate(
        output_file,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )

    # Define styles
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontSize=24,
        textColor=colors.HexColor("#1a1a1a"),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName="Helvetica-Bold",
    )

    h1_style = ParagraphStyle(
        "CustomH1",
        parent=styles["Heading1"],
        fontSize=18,
        textColor=colors.HexColor("#2c3e50"),
        spaceAfter=12,
        spaceBefore=20,
        fontName="Helvetica-Bold",
    )

    h2_style = ParagraphStyle(
        "CustomH2",
        parent=styles["Heading2"],
        fontSize=14,
        textColor=colors.HexColor("#34495e"),
        spaceAfter=10,
        spaceBefore=15,
        fontName="Helvetica-Bold",
    )

    h3_style = ParagraphStyle(
        "CustomH3",
        parent=styles["Heading3"],
        fontSize=12,
        textColor=colors.HexColor("#555555"),
        spaceAfter=8,
        spaceBefore=12,
        fontName="Helvetica-Bold",
    )

    body_style = ParagraphStyle(
        "CustomBody",
        parent=styles["BodyText"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=6,
        alignment=TA_JUSTIFY,
        leading=14,
    )

    bullet_style = ParagraphStyle(
        "CustomBullet",
        parent=styles["BodyText"],
        fontSize=10,
        textColor=colors.HexColor("#333333"),
        spaceAfter=4,
        leftIndent=20,
        bulletIndent=10,
        leading=14,
    )

    code_style = ParagraphStyle(
        "CustomCode",
        parent=styles["Code"],
        fontSize=9,
        textColor=colors.HexColor("#d63384"),
        fontName="Courier",
        backColor=colors.HexColor("#f8f9fa"),
        spaceAfter=4,
    )

    # Parse markdown and build story
    story = []
    lines = content.split("\n")
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        if not line:
            story.append(Spacer(1, 6))
            i += 1
            continue

        # Title (# at start)
        if line.startswith("# "):
            text = line[2:].strip()
            story.append(Paragraph(text, title_style))
            story.append(Spacer(1, 12))

        # H2 (## at start)
        elif line.startswith("## "):
            text = line[3:].strip()
            story.append(Paragraph(text, h1_style))
            story.append(Spacer(1, 8))

        # H3 (### at start)
        elif line.startswith("### "):
            text = line[4:].strip()
            story.append(Paragraph(text, h2_style))
            story.append(Spacer(1, 6))

        # H4 (#### at start)
        elif line.startswith("#### "):
            text = line[5:].strip()
            story.append(Paragraph(text, h3_style))
            story.append(Spacer(1, 4))

        # Bullet points
        elif line.startswith("- ") or line.startswith("* "):
            text = "• " + line[2:].strip()
            # Handle inline code
            text = re.sub(
                r"`([^`]+)`", r'<font name="Courier" color="#d63384">\1</font>', text
            )
            # Handle bold
            text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
            story.append(Paragraph(text, bullet_style))

        # Horizontal rule
        elif line.startswith("---"):
            story.append(Spacer(1, 12))
            story.append(PageBreak())

        # Regular paragraph
        else:
            text = line
            # Handle inline code
            text = re.sub(
                r"`([^`]+)`", r'<font name="Courier" color="#d63384">\1</font>', text
            )
            # Handle bold
            text = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", text)
            # Handle italic
            text = re.sub(r"\*([^*]+)\*", r"<i>\1</i>", text)

            story.append(Paragraph(text, body_style))

        i += 1

    # Add metadata footer
    story.append(Spacer(1, 30))
    story.append(Paragraph("---", body_style))
    footer_text = (
        f"<i>Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}</i>"
    )
    story.append(Paragraph(footer_text, body_style))
    footer_text2 = "<i>GHB Strategy Portfolio Selection Guide | Gold-Gray-Blue Weekly Trading System</i>"
    story.append(Paragraph(footer_text2, body_style))

    # Build PDF
    doc.build(story)

    return output_file


if __name__ == "__main__":
    try:
        print("📄 Generating GHB Strategy PDF Guide...")
        print("=" * 80)
        
        output_file = create_ghb_strategy_pdf()
        print(f"\n✅ PDF generated successfully!")
        print(f"📁 Location: {output_file}")
        print(f"📄 File size: {round(os.path.getsize(output_file) / 1024, 1)} KB")
        print("\n" + "=" * 80)
        print("You can now:")
        print("  1. Open the PDF to review GHB Strategy guide")
        print("  2. Print it for quick reference")
        print("  3. Share it across devices")
        print("=" * 80)

    except ImportError:
        print("❌ Error: reportlab library not found")
        print("\n📦 Please install reportlab:")
        print("   pip install reportlab")
        print("\nThen run this script again.")

    except Exception as e:
        print(f"❌ Error generating PDF: {str(e)}")
        import traceback

        traceback.print_exc()
