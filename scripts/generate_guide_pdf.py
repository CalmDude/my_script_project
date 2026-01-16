"""
Generate PDF from GHB_PORTFOLIO_SCANNER_GUIDE.md
"""

import markdown
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
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from pathlib import Path
import re


def remove_emojis(text):
    """Remove all emojis and replace with text equivalents"""
    emoji_map = {
        "✅": "[OK]",
        "❌": "[X]",
        "⚠️": "[!]",
        "🔴": "[CRITICAL]",
        "🟡": "[WARNING]",
        "🟢": "[OK]",
        "⚪": "",
        "🔵": "",
        "🟡": "",
        "⭐": "*",
        "🎯": "[TARGET]",
        "💰": "$",
        "💡": "TIP:",
        "📊": "",
        "📈": "",
        "📉": "",
        "📅": "",
        "📋": "",
        "📝": "",
        "📁": "",
        "📄": "",
        "📕": "",
        "🔥": "[HOT]",
        "🚨": "[ALERT]",
    }

    for emoji, replacement in emoji_map.items():
        text = text.replace(emoji, replacement)

    # Remove any remaining emojis (Unicode ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001f600-\U0001f64f"  # emoticons
        "\U0001f300-\U0001f5ff"  # symbols & pictographs
        "\U0001f680-\U0001f6ff"  # transport & map symbols
        "\U0001f1e0-\U0001f1ff"  # flags
        "\U00002702-\U000027b0"
        "\U000024c2-\U0001f251"
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub("", text)

    return text


# Read the markdown file
md_file = Path("../docs/GHB_PORTFOLIO_SCANNER_GUIDE.md")
with open(md_file, "r", encoding="utf-8") as f:
    md_content = f.read()

# Remove emojis from entire content
md_content = remove_emojis(md_content)

# Create PDF
pdf_file = Path("../docs/GHB_PORTFOLIO_SCANNER_GUIDE.pdf")
doc = SimpleDocTemplate(
    str(pdf_file),
    pagesize=letter,
    leftMargin=0.75 * inch,
    rightMargin=0.75 * inch,
    topMargin=0.75 * inch,
    bottomMargin=0.75 * inch,
)

story = []
styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    "Title",
    parent=styles["Heading1"],
    fontSize=24,
    textColor=colors.HexColor("#1f4788"),
    spaceAfter=6,
    alignment=TA_CENTER,
)
h1_style = ParagraphStyle(
    "H1",
    parent=styles["Heading1"],
    fontSize=16,
    textColor=colors.HexColor("#1f4788"),
    spaceAfter=12,
    spaceBefore=12,
)
h2_style = ParagraphStyle(
    "H2",
    parent=styles["Heading2"],
    fontSize=14,
    textColor=colors.HexColor("#0056b3"),
    spaceAfter=10,
    spaceBefore=10,
)
h3_style = ParagraphStyle(
    "H3",
    parent=styles["Heading3"],
    fontSize=12,
    textColor=colors.HexColor("#333"),
    spaceAfter=8,
    spaceBefore=8,
)
h4_style = ParagraphStyle(
    "H4",
    parent=styles["Heading4"],
    fontSize=11,
    textColor=colors.HexColor("#555"),
    spaceAfter=6,
    spaceBefore=6,
)
code_style = ParagraphStyle(
    "Code",
    parent=styles["Normal"],
    fontName="Courier",
    fontSize=8,
    textColor=colors.HexColor("#c7254e"),
    backColor=colors.HexColor("#f9f2f4"),
    leftIndent=20,
    rightIndent=20,
)

# Split content into lines
lines = md_content.split("\n")

in_code_block = False
code_lines = []
in_table = False
table_data = []

for line in lines:
    # Handle code blocks
    if line.startswith("```"):
        if in_code_block:
            # End code block
            if code_lines:
                code_text = "\n".join(code_lines)
                story.append(
                    Paragraph(
                        code_text.replace("<", "&lt;").replace(">", "&gt;"), code_style
                    )
                )
                story.append(Spacer(1, 0.1 * inch))
                code_lines = []
            in_code_block = False
        else:
            in_code_block = True
        continue

    if in_code_block:
        code_lines.append(line)
        continue

    # Skip empty lines outside structure
    if not line.strip():
        if story and not isinstance(story[-1], Spacer):
            story.append(Spacer(1, 0.1 * inch))
        continue

    # Main title
    if line.startswith("# GHB Portfolio Scanner"):
        story.append(Paragraph(line[2:], title_style))
        story.append(Spacer(1, 0.2 * inch))
        continue

    # Headers
    if line.startswith("#### "):
        story.append(Paragraph(line[5:], h4_style))
        continue
    elif line.startswith("### "):
        story.append(Paragraph(line[4:], h3_style))
        continue
    elif line.startswith("## "):
        # Add page break for major sections (except first few)
        if len(story) > 10:
            story.append(PageBreak())
        story.append(Paragraph(line[3:], h1_style))
        continue

    # Horizontal rules
    if line.strip() == "---":
        story.append(Spacer(1, 0.1 * inch))
        continue

    # Tables (simplified handling)
    if line.startswith("|") and "|" in line[1:]:
        # Basic table - just show as formatted text for now
        story.append(Paragraph(line.replace("|", " | "), styles["Normal"]))
        continue

    # Lists
    if line.startswith("- ") or line.startswith("* "):
        bullet_text = line[2:]
        # Convert markdown bold
        bullet_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", bullet_text)
        bullet_text = re.sub(
            r"`(.*?)`", r'<font face="Courier" color="#c7254e">\1</font>', bullet_text
        )
        story.append(Paragraph(f"• {bullet_text}", styles["Normal"]))
        continue

    # Numbered lists
    if re.match(r"^\d+\.", line):
        list_text = re.sub(r"^\d+\.\s*", "", line)
        list_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", list_text)
        list_text = re.sub(
            r"`(.*?)`", r'<font face="Courier" color="#c7254e">\1</font>', list_text
        )
        story.append(Paragraph(list_text, styles["Normal"]))
        continue

    # Regular paragraphs
    # Convert markdown formatting
    text = line
    text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)
    text = re.sub(r"`(.*?)`", r'<font face="Courier" color="#c7254e">\1</font>', text)

    if text.strip():
        story.append(Paragraph(text, styles["Normal"]))

# Build PDF
doc.build(story)

print(f"✅ PDF Generated: {pdf_file}")
print(f"   Converted from: {md_file}")
print(f"   Pages: {len([s for s in story if isinstance(s, PageBreak)]) + 1}")
