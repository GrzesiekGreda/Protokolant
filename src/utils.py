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
    doc = SimpleDocTemplate(filename, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=30,
        alignment=1  # Center
    )
    
    # Title
    story.append(Paragraph('PROTOKÓŁ ZE SPOTKANIA', title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Meeting details
    story.append(Paragraph(f'<b>Temat:</b> {protocol.title}', styles['Normal']))
    story.append(Paragraph(f'<b>Data:</b> {format_datetime_polish(protocol.date)}', styles['Normal']))
    if protocol.location:
        story.append(Paragraph(f'<b>Miejsce:</b> {protocol.location}', styles['Normal']))
    story.append(Spacer(1, 0.5*cm))
    
    # Participants
    if protocol.participants:
        story.append(Paragraph('<b>Uczestnicy:</b>', styles['Heading2']))
        for participant in protocol.participants:
            story.append(Paragraph(f'• {participant.name}', styles['Normal']))
        story.append(Spacer(1, 0.5*cm))
    
    # Agenda items
    if protocol.agenda_items:
        story.append(Paragraph('<b>Agenda:</b>', styles['Heading2']))
        for item in sorted(protocol.agenda_items, key=lambda x: x.order):
            story.append(Paragraph(f'<b>{item.title}</b>', styles['Normal']))
            if item.discussion:
                story.append(Paragraph(item.discussion, styles['Normal']))
            story.append(Spacer(1, 0.3*cm))
    
    # Action items
    if protocol.action_items:
        story.append(Paragraph('<b>Zadania:</b>', styles['Heading2']))
        for action in protocol.action_items:
            deadline_text = format_date_polish(action.deadline) if action.deadline else 'Brak terminu'
            story.append(Paragraph(
                f'• {action.description} (<b>Odpowiedzialny:</b> {action.assignee}, <b>Termin:</b> {deadline_text})',
                styles['Normal']
            ))
    
    doc.build(story)
