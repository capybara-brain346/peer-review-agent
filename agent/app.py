import streamlit as st
import tempfile
import os
from agent.agent import peer_reviewer
from agent.source_manager import SourceManager
from agent.memory import MemoryManager
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from agent.schemas import PeerReviewReport
from agent.utils.logger import logger

try:
    source_manager = SourceManager()
    memory_manager = MemoryManager()
except Exception as e:
    st.error(f"System Initialization Error: {e}")
    logger.critical(f"Failed to initialize managers in app: {e}")
    st.stop()

st.set_page_config(page_title="Peer Review Agent", layout="wide")


def generate_pdf(report: PeerReviewReport, filename: str):
    logger.info(f"Generating PDF report: {filename}")
    try:
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        title_style = styles["Title"]
        story.append(Paragraph("Peer Review Report", title_style))
        story.append(Spacer(1, 12))

        story.append(Paragraph("<b>Summary</b>", styles["Heading2"]))
        story.append(Paragraph(report.summary, styles["Normal"]))
        story.append(Spacer(1, 12))

        story.append(
            Paragraph("<b>Confidential Recommendation</b>", styles["Heading2"])
        )
        story.append(Paragraph(report.confidential_recommendation, styles["Normal"]))
        story.append(Spacer(1, 12))

        if report.major_issues:
            story.append(Paragraph("<b>Major Issues</b>", styles["Heading2"]))
            for issue in report.major_issues:
                text = f"<b>{issue.issue_type}:</b> {issue.description}<br/><i>Evidence: {issue.evidence}</i>"
                story.append(Paragraph(text, styles["Normal"]))
                story.append(Spacer(1, 6))
            story.append(Spacer(1, 12))

        if report.minor_issues:
            story.append(Paragraph("<b>Minor Issues</b>", styles["Heading2"]))
            for issue in report.minor_issues:
                story.append(Paragraph(f"- {issue}", styles["Normal"]))
            story.append(Spacer(1, 12))

        if report.line_by_line_comments:
            story.append(Paragraph("<b>Line-by-Line Comments</b>", styles["Heading2"]))
            data = [["Original Text", "Comment"]]
            for comment in report.line_by_line_comments:
                data.append(
                    [
                        Paragraph(comment.original_text, styles["Normal"]),
                        Paragraph(comment.comment, styles["Normal"]),
                    ]
                )

            table = Table(data, colWidths=[250, 250])
            table.setStyle(
                TableStyle(
                    [
                        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                        ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                        ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                        ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                        ("GRID", (0, 0), (-1, -1), 1, colors.black),
                    ]
                )
            )
            story.append(table)

        doc.build(story)
        logger.info("PDF generated successfully")
    except Exception as e:
        logger.error(f"PDF generation failed: {e}")
        st.error("Failed to generate PDF report.")


def main():
    st.title("Peer Review Agent")

    with st.sidebar:
        st.header("Configuration")
        blog_id = st.text_input("Project / Blog Name", value="My Tech Blog")

        st.divider()
        st.subheader("Source Material")
        uploaded_source = st.file_uploader(
            "Upload Source Text (.txt, .md)", type=["txt", "md"]
        )
        if uploaded_source:
            if st.button("Ingest Source"):
                try:
                    content = uploaded_source.read().decode("utf-8")
                    source_manager.add_source(content, uploaded_source.name)
                    st.success(f"Ingested {uploaded_source.name}")
                    logger.info(f"User ingested new source: {uploaded_source.name}")
                except Exception as e:
                    st.error(f"Failed to ingest source: {e}")
                    logger.error(f"Source ingestion error: {e}")

        sources = source_manager.list_sources()
        if sources:
            st.write("Available Sources:")
            for s in sources:
                st.text(f"- {s}")

    st.subheader("Blog Content")

    tab1, tab2 = st.tabs(["Text Input", "URL Input"])

    content_to_review = ""

    with tab1:
        text_input = st.text_area("Paste blog content here", height=300)
        if text_input:
            content_to_review = text_input

    with tab2:
        url_input = st.text_input("Enter blog URL")
        if url_input:
            content_to_review = url_input

    if st.button("Run Review"):
        if not content_to_review:
            st.error("Please provide content to review.")
            logger.warning("User attempted run without content")
            return

        with st.spinner("Reviewing content..."):
            try:
                logger.info(f"User initiated review for project: {blog_id}")
                report = peer_reviewer.review_blog(blog_id, content_to_review)

                st.divider()
                st.header("Review Report")

                st.subheader("Summary")
                st.write(report.summary)

                st.subheader("Recommendation")
                st.write(report.confidential_recommendation)

                if report.major_issues:
                    st.subheader("Major Issues")
                    for issue in report.major_issues:
                        with st.expander(f"{issue.issue_type}"):
                            st.write(f"**Description:** {issue.description}")
                            st.write(f"**Evidence:** {issue.evidence}")

                if report.minor_issues:
                    st.subheader("Minor Issues")
                    for issue in report.minor_issues:
                        st.write(f"- {issue}")

                if report.line_by_line_comments:
                    st.subheader("Line-by-Line Comments")
                    comment_data = [
                        {"Original": c.original_text, "Comment": c.comment}
                        for c in report.line_by_line_comments
                    ]
                    st.table(comment_data)

                with tempfile.NamedTemporaryFile(
                    delete=False, suffix=".pdf"
                ) as tmp_file:
                    generate_pdf(report, tmp_file.name)
                    with open(tmp_file.name, "rb") as f:
                        st.download_button(
                            label="Download PDF Report",
                            data=f,
                            file_name=f"review_report_{blog_id}.pdf",
                            mime="application/pdf",
                        )
                    os.unlink(tmp_file.name)

                logger.info("Review cycle completed successfully")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Review process failed: {e}")


if __name__ == "__main__":
    main()
