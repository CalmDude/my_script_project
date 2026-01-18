"""
Generate PDF from any markdown file
Usage: python generate_pdf_generic.py <input_markdown_file>
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
import sys


def remove_emojis(text):
    """Remove all emojis and replace with text equivalents"""
    emoji_map = {
        "✅": "[OK]",
        "❌": "[X]",
        "⚠️": "[!]",
        "🔴": "[CRITICAL]",
        "🟡": "[WARNING]",
        "🟢": "[GOOD]",
        "📈": "[CHART]",
        "💰": "[MONEY]",
        "📊": "[DATA]",
        "🎯": "[TARGET]",
        "🔍": "[SEARCH]",
        "💡": "[IDEA]",
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


# Get input file from command line
if len(sys.argv) < 2:
    print("Usage: python generate_pdf_generic.py <input_markdown_file>")
    sys.exit(1)

md_file = Path(sys.argv[1])
if not md_file.exists():
    print(f"Error: File not found: {md_file}")
    sys.exit(1)

# Read the markdown file
with open(md_file, "r", encoding="utf-8") as f:
    md_content = f.read()

# Remove emojis from entire content
md_content = remove_emojis(md_content)

# Create PDF (same name as input but with .pdf extension)
pdf_file = md_file.with_suffix(".pdf")
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

heading1_style = ParagraphStyle(
    "CustomHeading1",
    parent=styles["Heading1"],
    fontSize=18,
    textColor=colors.HexColor("#1f4788"),
    spaceBefore=12,
    spaceAfter=6,
)

heading2_style = ParagraphStyle(
    "CustomHeading2",
    parent=styles["Heading2"],
    fontSize=14,
    textColor=colors.HexColor("#2563eb"),
    spaceBefore=10,
    spaceAfter=4,
)

heading3_style = ParagraphStyle(
    "CustomHeading3",
    parent=styles["Heading3"],
    fontSize=12,
    textColor=colors.HexColor("#3b82f6"),
    spaceBefore=8,
    spaceAfter=3,
)

heading4_style = ParagraphStyle(
    "CustomHeading4",
    parent=styles["Heading3"],
    fontSize=11,
    textColor=colors.HexColor("#60a5fa"),
    spaceBefore=6,
    spaceAfter=2,
)

code_style = ParagraphStyle(
    "Code",
    parent=styles["Code"],
    fontSize=9,
    fontName="Courier",
    textColor=colors.HexColor("#dc2626"),
    backColor=colors.HexColor("#f3f4f6"),
    leftIndent=10,
    rightIndent=10,
    spaceBefore=4,
    spaceAfter=4,
)

# Split content into lines
lines = md_content.split("\n")
in_code_block = False
code_block_lines = []

for line in lines:
    # Handle code blocks
    if line.strip().startswith("```"):
        if in_code_block:
            # End of code block - render it
            code_text = "\n".join(code_block_lines)
            if code_text.strip():
                story.append(Paragraph(code_text, code_style))
            story.append(Spacer(1, 0.1 * inch))
            code_block_lines = []
            in_code_block = False
        else:
            # Start of code block
            in_code_block = True
        continue

    if in_code_block:
        code_block_lines.append(line)
        continue

    # Skip empty lines
    if not line.strip():
        story.append(Spacer(1, 0.1 * inch))
        continue

    # Handle horizontal rules
    if line.strip() in ["---", "***", "___"]:
        story.append(Spacer(1, 0.2 * inch))
        story.append(
            Table(
                [[""]],
                colWidths=[7 * inch],
                style=[("LINEABOVE", (0, 0), (-1, 0), 1, colors.grey)],
            )
        )
        story.append(Spacer(1, 0.2 * inch))
        continue

    # Handle headers
    if line.startswith("# "):
        text = remove_emojis(line[2:])
        story.append(Paragraph(text, title_style))
        story.append(Spacer(1, 0.2 * inch))
        continue

    if line.startswith("## "):
        text = remove_emojis(line[3:])
        story.append(Paragraph(text, heading1_style))
        continue

    if line.startswith("### "):
        text = remove_emojis(line[4:])
        story.append(Paragraph(text, heading2_style))
        continue

    if line.startswith("#### "):
        text = remove_emojis(line[5:])
        story.append(Paragraph(text, heading3_style))
        continue

    if line.startswith("##### "):
        text = remove_emojis(line[6:])
        story.append(Paragraph(text, heading4_style))
        continue

    # Handle bullet lists
    if line.strip().startswith("- ") or line.strip().startswith("* "):
        list_text = line.strip()[2:]
        list_text = "• " + list_text
        # Convert markdown formatting
        list_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", list_text)
        list_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", list_text)
        list_text = re.sub(
            r"`(.*?)`", r'<font face="Courier" color="#c7254e">\1</font>', list_text
        )
        story.append(Paragraph(list_text, styles["Normal"]))
        continue

    # Handle checkbox lists
    if "[ ]" in line or "[x]" in line or "[X]" in line:
        list_text = line.strip()
        list_text = (
            list_text.replace("- [ ]", "☐").replace("- [x]", "☑").replace("- [X]", "☑")
        )
        list_text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", list_text)
        list_text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", list_text)
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
