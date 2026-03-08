import base64
import io

from fpdf import FPDF

from app.models.consent import ConsentFormRequest


class _ConsentPdf(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 14)
        self.cell(0, 10, "KameArt \u2014 Consentimiento Informado", align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(30, 30, 30)
        self.line(self.l_margin, self.get_y(), self.w - self.r_margin, self.get_y())
        self.ln(3)

    def footer(self):
        self.set_y(-12)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(130, 130, 130)
        self.cell(0, 8, f"P\u00e1gina {self.page_no()}", align="C")
        self.set_text_color(0, 0, 0)


def _section(pdf: _ConsentPdf, title: str) -> None:
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_fill_color(30, 30, 30)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, f"  {title}", fill=True, new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Helvetica", "", 10)
    pdf.ln(2)


def _field(pdf: _ConsentPdf, label: str, value: str) -> None:
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(65, 6, f"{label}:", new_x="END")
    pdf.set_font("Helvetica", "", 10)
    pdf.multi_cell(0, 6, str(value), new_x="LMARGIN", new_y="NEXT")


def _check(pdf: _ConsentPdf, label: str, accepted: bool) -> None:
    mark = "[SI]" if accepted else "[NO]"
    pdf.set_font("Helvetica", "B", 10)
    pdf.cell(65, 6, f"{label}:", new_x="END")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, mark, new_x="LMARGIN", new_y="NEXT")


class PdfService:
    """Generates a PDF document from a consent form submission."""

    def generate(self, form: ConsentFormRequest, reference: str, timestamp: str) -> bytes:
        pdf = _ConsentPdf()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # Reference line
        pdf.set_font("Helvetica", "", 9)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, f"Referencia: {reference}   |   Registrado: {timestamp}", align="C", new_x="LMARGIN", new_y="NEXT")
        pdf.set_text_color(0, 0, 0)
        pdf.ln(4)

        # ── Personal data ──────────────────────────────────────────────────────
        pd = form.personal_data
        _section(pdf, "Datos Personales")
        _field(pdf, "Nombre completo", pd.full_name)
        _field(pdf, "Tipo de documento", pd.document_type)
        _field(pdf, "N\u00famero de documento", pd.document_id)
        _field(pdf, "Fecha de nacimiento", str(pd.date_of_birth))
        _field(pdf, "Correo electr\u00f3nico", pd.email)
        _field(pdf, "Tel\u00e9fono", pd.phone)
        _field(pdf, "Direcci\u00f3n", pd.address)
        _field(pdf, "Ciudad", pd.city)
        pdf.ln(2)
        _field(pdf, "Contacto de emergencia", pd.emergency_contact_name)
        _field(pdf, "Tel\u00e9fono emergencia", pd.emergency_contact_phone)
        pdf.ln(4)

        # ── Consent text ───────────────────────────────────────────────────────
        _section(pdf, "Documento de Consentimiento Informado")
        pdf.set_font("Helvetica", "", 9)
        consent_text = (
            "El/la cliente declara libre y voluntariamente que desea realizarse un procedimiento de "
            "tatuaje y/o perforaci\u00f3n corporal (piercing) en el estudio KameArt, conociendo la naturaleza "
            "del procedimiento (introducci\u00f3n de pigmentos en la dermis o perforaci\u00f3n de tejido mediante "
            "material est\u00e9ril de un solo uso), los riesgos asociados (infecci\u00f3n, reacciones al\u00e9rgicas, "
            "queloides, sangrado, inflamaci\u00f3n), la permanencia e irreversibilidad del tatuaje, y el "
            "requisito de representante legal para menores de edad. Declara no encontrarse bajo efectos "
            "de alcohol o sustancias psicoactivas y que su estado de salud es apto para el procedimiento."
        )
        pdf.multi_cell(0, 5, consent_text, new_x="LMARGIN", new_y="NEXT")
        pdf.ln(4)

        # ── Checkboxes ─────────────────────────────────────────────────────────
        cd = form.consent_data
        _section(pdf, "Declaraciones y Autorizaciones")
        _check(pdf, "Le\u00ed y comprend\u00ed el consentimiento", cd.has_read_information)
        _check(pdf, "Consiento el procedimiento", cd.consents_to_procedure)
        _check(pdf, "Autorizo tratamiento de datos (Ley 1581/2012)", cd.authorizes_data_processing)
        _check(pdf, "Autorizo registro fotogr\u00e1fico (opcional)", cd.authorizes_media)
        pdf.ln(2)
        _field(pdf, "Lugar de firma", cd.place)
        _field(pdf, "Fecha de firma", str(cd.signature_date))
        pdf.ln(4)

        # ── Signature image ────────────────────────────────────────────────────
        _section(pdf, "Firma Digital")
        pdf.ln(2)
        raw = form.signature_image.split(",")[-1]
        img_bytes = base64.b64decode(raw)
        pdf.image(io.BytesIO(img_bytes), w=80)

        return bytes(pdf.output())


pdf_service = PdfService()
