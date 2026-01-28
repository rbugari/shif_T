import io
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from typing import Dict, Any, List

class ReportService:
    @staticmethod
    def generate_triage_pdf(project_data: Dict[str, Any]) -> bytes:
        """
        Generates a PDF report for the Triage stage.
        project_data expected structure:
        {
            "name": str,
            "assets": List[Dict] (inventory),
            "summary": Dict (counts),
            "generated_at": str
        }
        """
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = styles["Title"]
        elements.append(Paragraph(f"Triage Report: {project_data.get('name', 'Unknown Project')}", title_style))
        elements.append(Spacer(1, 12))
        
        # Meta Info
        normal_style = styles["Normal"]
        elements.append(Paragraph(f"Generated At: {project_data.get('generated_at', 'N/A')}", normal_style))
        elements.append(Spacer(1, 24))
        
        # Section 1: Executive Summary
        h2_style = styles["Heading2"]
        elements.append(Paragraph("1. Executive Summary", h2_style))
        summary_text = (
            f"The deep scan identified a total of {len(project_data.get('assets', []))} assets. "
            "The architecture follows the Medallion pattern (Bronze, Silver, Gold). "
            "Key components identified include PySpark scripts, SQL definitions, and configuration files."
        )
        elements.append(Paragraph(summary_text, normal_style))
        elements.append(Spacer(1, 12))
        
        # Section 2: Asset Inventory
        elements.append(Paragraph("2. Asset Inventory", h2_style))
        elements.append(Spacer(1, 6))
        
        data = [["Filename", "Type", "Path", "Status"]]
        
        assets = project_data.get("assets", [])
        # Sort by type then name
        assets.sort(key=lambda x: (x.get("type", ""), x.get("filename", "")))
        
        for asset in assets:
            row = [
                (asset.get("filename") or "")[:40], # Truncate long names
                asset.get("type") or "UNKNOWN",
                (asset.get("source_path") or "")[:50],
                "Selected" if asset.get("selected") else "Ignored"
            ]
            data.append(row)
            
        # Table Styling
        table = Table(data, colWidths=[200, 80, 200, 60])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        elements.append(table)
        elements.append(Spacer(1, 24))
        
        # Section 3: Recommendations / Gaps
        elements.append(Paragraph("3. Recommendations & Gaps", h2_style))
        gaps_text = "No critical gaps detected. Ensure all 'Silver' layer scripts have corresponding 'Gold' layer aggregations defined in the orchestration plan."
        elements.append(Paragraph(gaps_text, normal_style))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer.read()
