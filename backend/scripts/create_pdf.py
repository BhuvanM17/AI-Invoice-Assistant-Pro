import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch


def create_bizzhub_pdf_once():
    """Run this function ONCE to create the PDF file"""
    pdf_filename = "bizzhub_workspaces.pdf"

    # Check if PDF already exists
    if os.path.exists(pdf_filename):
        print(f"✅ PDF already exists: {pdf_filename}")
        return pdf_filename

    print(f"📄 Creating PDF: {pdf_filename}")

    # Create document
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)
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
        fontSize=16,
        spaceAfter=12,
        textColor=colors.HexColor('#3498db')
    )

    # Content
    content = []

    # Title
    content.append(Paragraph("BizzHub Workspaces - Complete Information", title_style))
    content.append(Spacer(1, 20))

    # Company Overview
    content.append(Paragraph("Company Overview", heading_style))
    overview = """
    BizzHub Workspaces was conceptualized with a goal to provide great vibrant interiors 
    with flexible layouts and terms at reasonable costing. BizzHub provides Managed Offices 
    and Co-Working spaces that connect with people of all ages and are suitable for all 
    market segments like Start-ups, MSMEs, Corporates and Multinationals alike.

    With over 7 years of experience, we have a proven track-record of providing high quality 
    office spaces with services matching industry standards. All our centres across Bengaluru 
    are favourites among our esteemed clients.

    Awards & Recognition:
    • Top 10 Best Co-Working Service Providers - CEO Insights (2019 & 2020)
    • Excellence in Workspace Design - 2021
    • Best Flexible Workspace Provider - 2022
    """
    content.append(Paragraph(overview, styles['Normal']))
    content.append(Spacer(1, 20))

    # Services Table
    content.append(Paragraph("Services & Amenities", heading_style))
    services = [
        ["Service", "Description", "Availability", "Price Range"],
        ["Co-Working (Hot Desk)", "Flexible seating, community area", "All centers", "₹8,000 - ₹12,000/month"],
        ["Dedicated Desk", "Personal desk, 24/7 access", "All centers", "₹10,000 - ₹15,000/month"],
        ["Private Cabin (2-4p)", "Lockable private office", "Koramangala, Whitefield", "₹25,000 - ₹40,000/month"],
        ["Team Suite (5-10p)", "Custom layout, meeting room", "All centers", "₹60,000 - ₹90,000/month"],
        ["Virtual Office", "Business address, mail handling", "All centers", "₹2,000 - ₹5,000/month"],
        ["Meeting Room (Hourly)", "Fully equipped, projector", "All centers", "₹500 - ₹1,500/hour"],
        ["Day Pass", "Daily access, basic amenities", "All centers", "₹800 - ₹1,200/day"]
    ]

    services_table = Table(services, colWidths=[1.8 * inch, 2.5 * inch, 1.2 * inch, 1.5 * inch])
    services_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(services_table)
    content.append(Spacer(1, 20))

    # Locations
    content.append(Paragraph("Bangalore Locations", heading_style))
    locations = [
        ["Center", "Address", "Contact", "Features", "Parking"],
        ["Koramangala Hub", "3rd Block, 80ft Road", "080-4111-2222", "24/7, Cafe, Gym", "Yes (₹1000/month)"],
        ["Whitefield Tech Park", "ITPL Main Road", "080-4111-3333", "EV Charging, Events", "Yes (₹1500/month)"],
        ["Electronic City", "Phase 1, Near Infosys", "080-4111-4444", "Shuttle, Food Court", "Yes (₹800/month)"],
        ["Indiranagar", "100ft Road, Double Road", "080-4111-5555", "Lounge, Terrace", "Limited (₹1200/month)"],
        ["MG Road", "Brigade Road Cross", "080-4111-6666", "Premium, Concierge", "Valet (₹2000/month)"]
    ]

    loc_table = Table(locations, colWidths=[1.5 * inch, 2 * inch, 1.2 * inch, 1.8 * inch, 1.2 * inch])
    loc_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2ecc71')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    content.append(loc_table)
    content.append(Spacer(1, 20))

    # Pricing Details
    content.append(Paragraph("Detailed Pricing", heading_style))
    pricing = """
    Standard Pricing (Exclusive of 18% GST):

    1. Co-Working Memberships:
       • Day Pass: ₹800 - ₹1,200 per day
       • 5-Day Plan: ₹3,500 - ₹5,000 per month
       • Full Month: ₹8,000 - ₹12,000 per month

    2. Private Offices:
       • 2-person cabin: ₹25,000 - ₹35,000/month
       • 4-person cabin: ₹40,000 - ₹55,000/month
       • 6-person suite: ₹65,000 - ₹85,000/month
       • 10+ person: Custom quote available

    3. Additional Services:
       • Parking: ₹800 - ₹2,000/month (varies by location)
       • Dedicated Internet: ₹1,500/month
       • Mail Handling: ₹500/month
       • Custom Branding: One-time ₹5,000 setup

    4. Meeting Rooms:
       • 4-person: ₹500/hour or ₹3,000/day
       • 8-person: ₹800/hour or ₹5,000/day
       • 12-person: ₹1,200/hour or ₹7,000/day

    Note: All prices are subject to change. Minimum contract: 1 month.
    Security deposit: 1 month rent. Custom layouts available at additional cost.
    """
    content.append(Paragraph(pricing, styles['Normal']))
    content.append(Spacer(1, 20))

    # FAQs
    content.append(Paragraph("Frequently Asked Questions", heading_style))
    faqs = [
        ("What's included in the membership?",
         "Workspace, high-speed WiFi, printing (100 pages/month), tea/coffee, access to common areas, community events."),
        ("Can I get a custom office layout?",
         "Yes, custom layouts available with one-time setup fee of ₹5,000-₹20,000 depending on complexity."),
        ("Is parking available at all centers?",
         "Yes, parking available at all centers. Prices vary: ₹800-₹2,000/month."),
        ("What are the payment terms?",
         "Monthly invoicing, payment within 7 days. Accept UPI, bank transfer, cards. Security deposit required."),
        ("Can I access other centers?",
         "Yes, with All-Access Pass (+₹2,000/month). Otherwise, access only to your home center."),
        ("Is there 24/7 access?",
         "Yes, for Dedicated Desk and Private Office members. Co-working members: 8 AM - 10 PM."),
        ("What's your cancellation policy?",
         "30-day notice period. Security deposit refunded within 15 days of vacating."),
        ("Do you provide IT support?",
         "Yes, basic IT support included. Advanced support available at ₹1,500/month."),
        ("Are pets allowed?",
         "Only in designated pet-friendly zones at Koramangala and Indiranagar centers."),
        ("Do you have EV charging?",
         "Available at Whitefield and Electronic City centers. ₹100/hour charging.")
    ]

    for i, (q, a) in enumerate(faqs, 1):
        content.append(Paragraph(f"<b>Q{i}: {q}</b>", styles['Normal']))
        content.append(Paragraph(a, styles['Normal']))
        content.append(Spacer(1, 8))

    # Build PDF
    doc.build(content)
    print(f"✅ PDF created: {pdf_filename} ({os.path.getsize(pdf_filename)} bytes)")
    return pdf_filename

if __name__ == "__main__":
    create_bizzhub_pdf_once()
