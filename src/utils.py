"""
Utility functions for Protokolant application
"""

from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors

def format_date_polish(date_obj: datetime) -> str:
    """
    Format date to Polish format (DD.MM.YYYY)
    
    Args:
        date_obj: datetime object to format
    
    Returns:
        Formatted date string
    """
    return date_obj.strftime('%d.%m.%Y')

def format_datetime_polish(datetime_obj: datetime) -> str:
    """
    Format datetime to Polish format (DD.MM.YYYY HH:MM)
    
    Args:
        datetime_obj: datetime object to format
    
    Returns:
        Formatted datetime string
    """
    return datetime_obj.strftime('%d.%m.%Y %H:%M')

def generate_protocol_pdf(protocol, filename: str) -> None:
    """
    Generate PDF document from protocol
    
    Args:
        protocol: Protocol model instance
        filename: Output filename for PDF
    """
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.lib.enums import TA_CENTER
    import os
    
    # Register fonts supporting Polish characters
    try:
        # Get Windows fonts directory
        fonts_dir = os.path.join(os.environ.get('WINDIR', 'C:\\Windows'), 'Fonts')
        
        # Try Arial (available on Windows)
        arial_path = os.path.join(fonts_dir, 'arial.ttf')
        arial_bold_path = os.path.join(fonts_dir, 'arialbd.ttf')
        
        if os.path.exists(arial_path):
            pdfmetrics.registerFont(TTFont('CustomFont', arial_path))
            pdfmetrics.registerFont(TTFont('CustomFont-Bold', arial_bold_path))
            default_font = 'CustomFont'
            bold_font = 'CustomFont-Bold'
        else:
            # Fallback to Helvetica
            default_font = 'Helvetica'
            bold_font = 'Helvetica-Bold'
    except Exception as e:
        # Fallback to Helvetica
        default_font = 'Helvetica'
        bold_font = 'Helvetica-Bold'
    
    doc = SimpleDocTemplate(filename, pagesize=A4, leftMargin=2*cm, rightMargin=2*cm, topMargin=2*cm, bottomMargin=2*cm)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles for Polish characters
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontName=bold_font,
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontName=bold_font,
        fontSize=14,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12,
        spaceBefore=12
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontName=default_font,
        fontSize=11,
        leading=14
    )
    
    bold_normal_style = ParagraphStyle(
        'CustomBold',
        parent=styles['Normal'],
        fontName=bold_font,
        fontSize=11,
        leading=14
    )
    
    # Title
    story.append(Paragraph('PROTOKÓŁ ZE SPOTKANIA', title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Meeting details
    story.append(Paragraph(f'<font name="{bold_font}">Temat:</font> {protocol.title}', normal_style))
    story.append(Paragraph(f'<font name="{bold_font}">Data:</font> {format_datetime_polish(protocol.date)}', normal_style))
    if protocol.location:
        story.append(Paragraph(f'<font name="{bold_font}">Miejsce:</font> {protocol.location}', normal_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Participants
    if protocol.participants:
        story.append(Paragraph('Uczestnicy:', heading_style))
        for participant in protocol.participants:
            story.append(Paragraph(f'• {participant.name}', normal_style))
        story.append(Spacer(1, 0.5*cm))
    
    # Agenda items
    if protocol.agenda_items:
        story.append(Paragraph('Porządek obrad:', heading_style))
        for item in sorted(protocol.agenda_items, key=lambda x: x.order):
            story.append(Paragraph(f'<font name="{bold_font}">{item.title}</font>', normal_style))
            if item.discussion:
                story.append(Paragraph(item.discussion, normal_style))
            story.append(Spacer(1, 0.3*cm))
    
    # Action items
    if protocol.action_items:
        story.append(Paragraph('Zadania do wykonania:', heading_style))
        for action in protocol.action_items:
            deadline_text = format_date_polish(action.deadline) if action.deadline else 'Brak terminu'
            assignee_text = action.assignee if action.assignee else 'Nieprzypisane'
            story.append(Paragraph(
                f'• {action.description} (<font name="{bold_font}">Odpowiedzialny:</font> {assignee_text}, <font name="{bold_font}">Termin:</font> {deadline_text})',
                normal_style
            ))
    
    doc.build(story)
