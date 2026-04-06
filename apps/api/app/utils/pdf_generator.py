import re

from fpdf import FPDF

from app.core.logger import get_logger

logger = get_logger(__name__)


class PDFGenerator(FPDF):
    def header(self):
        self.set_y(12)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", 0, 0, "C")

    def section_heading(self, text: str):
        self.ln(2)
        self.set_font("helvetica", "B", 12)
        self.set_text_color(22, 78, 99)
        self.cell(0, 8, text.upper(), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(203, 213, 225)
        y = self.get_y()
        self.line(self.l_margin, y, self.w - self.r_margin, y)
        self.ln(3)
        self.set_font("helvetica", size=10.5)
        self.set_text_color(30, 41, 59)

    def body_text(self, text: str):
        self.multi_cell(0, 5.2, text, new_x="LMARGIN", new_y="NEXT")

    def bullet_text(self, text: str):
        self.multi_cell(0, 5.2, f"- {text}", new_x="LMARGIN", new_y="NEXT")


def sanitize_text(text: str) -> str:
    import unicodedata
    if not text:
        return ""
    
    # Common manual replacements for symbols not handled well by normalization
    replacements = {
        "\u2013": "-",
        "\u2014": "--",
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2022": "*",
        "\u2026": "...",
        "\u03bc": "u", # Greek Mu
        "\u039c": "M", # Greek Capital Mu
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
        
    # Normalize unicode (converts accented chars to base chars like é -> e)
    nfkd_form = unicodedata.normalize('NFKD', text)
    text = "".join([c for c in nfkd_form if not unicodedata.combining(c)])
    
    # Final safety: encode to latin-1 and ignore anything else to prevent FPDF helvetica crashes
    return text.encode("latin-1", "ignore").decode("latin-1")


def strip_markdown(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"__(.*?)__", r"\1", text)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[(.*?)\]\((.*?)\)", r"\1 (\2)", text)
    return re.sub(r"\s+", " ", text).strip()


def is_rule_line(text: str) -> bool:
    compact = text.replace(" ", "")
    if len(compact) < 3:
        return False
    return all(ch == "=" for ch in compact) or all(ch == "-" for ch in compact)


def looks_like_contact_line(text: str) -> bool:
    lowered = text.lower()
    markers = ("email", "phone", "linkedin", "github", "portfolio", "location", "@", "www.", "http")
    return any(marker in lowered for marker in markers)


def generate_resume_pdf(markdown_text: str) -> bytes:
    pdf = PDFGenerator()
    pdf.alias_nb_pages()
    pdf.set_margins(16, 14, 16)
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("helvetica", size=10.5)
    pdf.set_text_color(30, 41, 59)

    raw_lines = [sanitize_text(line.rstrip()) for line in markdown_text.splitlines()]
    lines = [line.strip() for line in raw_lines]

    name = ""
    contact_lines: list[str] = []
    body_start = 0

    for idx, raw_line in enumerate(lines):
        if not raw_line or is_rule_line(raw_line):
            continue

        text = strip_markdown(raw_line)
        if (
            not text
            or text.lower().startswith("tailored resume for")
            or text.lower().startswith("here's the tailored resume")
            or text.lower().startswith("here is the tailored resume")
        ):
            continue

        if not name:
            name = text
            body_start = idx + 1
            continue

        if looks_like_contact_line(text) or text.lower().startswith("contact information"):
            if not text.lower().startswith("contact information"):
                contact_lines.append(text)
            body_start = idx + 1
            continue

        break

    if not name:
        name = "Tailored Resume"

    pdf.set_font("helvetica", "B", 18)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(0, 9, name, new_x="LMARGIN", new_y="NEXT")

    if contact_lines:
        pdf.set_font("helvetica", size=10)
        pdf.set_text_color(71, 85, 105)
        pdf.body_text(" | ".join(contact_lines))
        pdf.ln(2)

    current_section = None

    for raw_line in lines[body_start:]:
        if not raw_line or is_rule_line(raw_line):
            continue

        if raw_line.startswith("#"):
            heading = strip_markdown(raw_line.lstrip("#").strip())
            if heading:
                current_section = heading
                pdf.section_heading(heading)
            continue

        if re.fullmatch(r"\*\*.+\*\*", raw_line):
            heading = strip_markdown(raw_line)
            if heading.lower().startswith("tailored resume for") or heading.lower().startswith("contact information"):
                continue
            current_section = heading
            pdf.section_heading(heading)
            continue

        if (raw_line.startswith("* ") or raw_line.startswith("- ")) and len(raw_line) > 2:
            bullet = strip_markdown(raw_line[2:].strip())
            if bullet:
                if current_section is None:
                    current_section = "Experience"
                    pdf.section_heading(current_section)
                pdf.bullet_text(bullet)
            continue

        text = strip_markdown(raw_line)
        if not text or looks_like_contact_line(text):
            continue

        if (
            text.lower().startswith("here's the tailored resume")
            or text.lower().startswith("here is the tailored resume")
        ):
            continue

        if current_section is None:
            current_section = "Summary"
            pdf.section_heading(current_section)

        pdf.body_text(" | ".join(part.strip() for part in text.split("|") if part.strip()))

    return bytes(pdf.output())
