from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from agent.schemas import PeerReviewReport
from agent.utils.logger import logger

def generate_pdf(report: PeerReviewReport, filename: str):
    """Generates a PDF report from the PeerReviewReport object."""
    logger.info(f"Generating PDF report: {filename}")
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title
        title_style = styles['Title']
        story.append(Paragraph("Peer Review Report", title_style))
        story.append(Spacer(1, 12))

        # Summary
        story.append(Paragraph("<b>Summary</b>", styles['Heading2']))
        story.append(Paragraph(report.summary, styles['Normal']))
        story.append(Spacer(1, 12))

        # Confidential Recommendation
        story.append(Paragraph("<b>Confidential Recommendation</b>", styles['Heading2']))
        story.append(Paragraph(report.confidential_recommendation, styles['Normal']))
        story.append(Spacer(1, 12))

        # Major Issues
        if report.major_issues:
            story.append(Paragraph("<b>Major Issues</b>", styles['Heading2']))
            for issue in report.major_issues:
                text = f"<b>{issue.issue_type}:</b> {issue.description}<br/><i>Evidence: {issue.evidence}</i>"
                story.append(Paragraph(text, styles['Normal']))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 12))

        # Minor Issues
        if report.minor_issues:
            story.append(Paragraph("<b>Minor Issues</b>", styles['Heading2']))
            for issue in report.minor_issues:
                story.append(Paragraph(f"- {issue}", styles['Normal']))
            story.append(Spacer(1, 12))

        # Line-by-Line Comments
        if report.line_by_line_comments:
            story.append(Paragraph("<b>Line-by-Line Comments</b>", styles['Heading2']))
            data = [["Original Text", "Comment"]]
            for comment in report.line_by_line_comments:
                data.append([Paragraph(comment.original_text, styles['Normal']), 
                             Paragraph(comment.comment, styles['Normal'])])
            
            table = Table(data, colWidths=[250, 250])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ]))
            story.append(table)

        doc.build(story)
        logger.info("PDF generated successfully")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        raise

