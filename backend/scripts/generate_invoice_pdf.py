import os
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from ..core.models import InvoiceSchema


def create_invoice_pdf(invoice_data: dict, filename: str = None):
    """
    Creates a professional invoice PDF from invoice data

    Args:
        invoice_data (dict): Invoice data dictionary
        filename (str): Output filename (optional, will be generated if not provided)

    Returns:
        str: Path to the created PDF file
    """
    if filename is None:
        invoice_number = invoice_data.get('invoice_number', 'DRAFT')
        filename = f"invoice_{invoice_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

    # Ensure the output directory exists
    output_dir = os.path.join(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))), "data")
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, filename)

    # Create document
    doc = SimpleDocTemplate(filepath, pagesize=letter)
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        spaceAfter=30,
        textColor=colors.HexColor('#2c3e50')
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        textColor=colors.HexColor('#3498db')
    )

    # Content
    content = []

    # Title
    content.append(Paragraph(
        f"Invoice #{invoice_data.get('invoice_number', 'DRAFT')}", title_style))
    content.append(Spacer(1, 20))

    # Invoice Info Table
    invoice_info = [
        ["Invoice Date", invoice_data.get(
            'invoice_date', datetime.now().strftime('%Y-%m-%d'))],
        ["Due Date", invoice_data.get('due_date', '')],
        ["Currency", invoice_data.get('currency', 'INR')],
    ]

    invoice_info_table = Table(invoice_info, colWidths=[2 * inch, 3 * inch])
    invoice_info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(invoice_info_table)
    content.append(Spacer(1, 20))

    # Customer Info
    content.append(Paragraph("Bill To:", heading_style))
    customer_info = [
        [invoice_data.get('customer_name', ''), ""],
        [invoice_data.get('customer_email', ''), ""],
        [f"GSTIN: {invoice_data.get('customer_gst', 'N/A')}", ""],
    ]

    customer_table = Table(customer_info, colWidths=[3 * inch, 2 * inch])
    customer_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('TOPPADDING', (0, 0), (-1, -1), 1),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 1),
    ]))
    content.append(customer_table)
    content.append(Spacer(1, 20))

    # Line Items
    content.append(Paragraph("Items:", heading_style))

    # Items table header
    items_header = [["Item", "Qty", "Unit Price", "Total"]]
    items_data = items_header.copy()

    for item in invoice_data.get('items', []):
        items_data.append([
            item['name'],
            f"{item['quantity']:g}",
            f"₹{item['unit_price']:.2f}",
            f"₹{item['quantity'] * item['unit_price']:.2f}"
        ])

    # Add totals
    items_data.append(
        ["", "", "Subtotal:", f"₹{invoice_data.get('subtotal', 0):.2f}"])
    items_data.append(
        ["", "", f"Tax ({invoice_data.get('tax_percent', 0):g}%):", f"₹{invoice_data.get('tax_amount', 0):.2f}"])
    items_data.append(
        ["", "", "Shipping:", f"₹{invoice_data.get('shipping_fee', 0):.2f}"])
    items_data.append(
        ["", "", "Discount:", f"-₹{invoice_data.get('discount', 0):.2f}"])
    items_data.append(
        ["", "", "Grand Total:", f"₹{invoice_data.get('grand_total', 0):.2f}"])

    items_table = Table(items_data, colWidths=[
                        2.5 * inch, 0.8 * inch, 1.2 * inch, 1.2 * inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -5), colors.beige),  # Items rows
        ('BACKGROUND', (-2, -4), (-1, -1),
         colors.HexColor('#ecf0f1')),  # Summary rows
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (-2, -4), (-1, -1), 'Helvetica-Bold'),  # Bold summary rows
    ]))
    content.append(items_table)
    content.append(Spacer(1, 20))

    # Terms and conditions
    content.append(Paragraph("Terms & Conditions:", heading_style))
    terms = "Payment is due within 30 days. Late payments may incur additional fees. Thank you for your business!"
    content.append(Paragraph(terms, styles['Normal']))

    # Build PDF
    doc.build(content)
    print(f"✅ Invoice PDF created: {filepath}")
    return filepath


def create_invoice_from_schema(invoice_schema: InvoiceSchema, filename: str = None):
    """
    Creates a professional invoice PDF from an InvoiceSchema object

    Args:
        invoice_schema (InvoiceSchema): Invoice schema object
        filename (str): Output filename (optional)

    Returns:
        str: Path to the created PDF file
    """
    return create_invoice_pdf(invoice_schema.to_dict(), filename)


if __name__ == "__main__":
    # Example usage
    sample_invoice = {
        "invoice_number": "INV-001",
        "customer_name": "John Doe",
        "customer_email": "john@example.com",
        "customer_gst": "12ABCDE1234F1Z5",
        "invoice_date": "2023-12-01",
        "due_date": "2023-12-31",
        "currency": "INR",
        "tax_percent": 18.0,
        "shipping_fee": 100.0,
        "discount": 50.0,
        "discount_code": "SAVE50",
        "items": [
            {"name": "T-Shirt", "quantity": 2, "unit_price": 500.0},
            {"name": "Jeans", "quantity": 1, "unit_price": 1200.0}
        ],
        "subtotal": 2200.0,
        "tax_amount": 396.0,
        "grand_total": 2546.0
    }

    create_invoice_pdf(sample_invoice, "sample_invoice.pdf")
