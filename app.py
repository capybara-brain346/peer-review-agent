import streamlit as st
import tempfile
import os
import json
from dotenv import load_dotenv
import asyncio
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.genai import types as genai_types

from agent.agent import peer_review_agent
from agent.source_manager import SourceManager
from agent.schemas import PeerReviewReport
from agent.memory import MemoryManager
from agent.utils.logger import logger
from agent.utils.pdf_generator import generate_pdf

load_dotenv()

try:
    source_manager = SourceManager()
    memory_manager = MemoryManager()

    async def run_peer_review_async(blog_id: str, content: str) -> PeerReviewReport:
        logger.info(f"Starting async peer review for blog_id: {blog_id}")

        memory_manager = await asyncio.to_thread(MemoryManager)

        past_feedback = await asyncio.to_thread(
            memory_manager.get_blog_history, blog_id
        )
        past_feedback_text = (
            json.dumps(past_feedback)
            if past_feedback
            else "No previous feedback available."
        )
        logger.debug(f"Retrieved {len(past_feedback)} past feedback items")

        session_id = f"session_{blog_id}"
        session_service = InMemorySessionService()
        await session_service.create_session(
            app_name="peer_review_app", user_id=blog_id, session_id=session_id
        )

        runner = Runner(
            agent=peer_review_agent,
            app_name="agent",
            session_service=session_service,
        )

        review_prompt = f"""Please review the following blog content:

    **Blog Content:**
    {content}

    **Past Feedback Context:**
    {past_feedback_text}

    **Source Context:**
    Use the retrieve_source_context tool to search through the uploaded source documents and verify information against them.

    Provide a comprehensive peer review report following the output schema requirements."""

        logger.info("Executing runner.run_async")

        full_response = ""
        report = None

        async for event in runner.run_async(
            user_id=blog_id,
            session_id=session_id,
            new_message=genai_types.Content(
                role="user", parts=[genai_types.Part.from_text(text=review_prompt)]
            ),
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    full_response = event.content.parts[0].text
                    logger.debug(
                        f"Received final response: {len(full_response)} characters"
                    )

                if hasattr(event, "structured_response") and event.structured_response:
                    report = event.structured_response
                    logger.info(
                        "Successfully received structured PeerReviewReport from agent"
                    )
                break

        if not report and not full_response:
            logger.error("No response received from agent")
            raise ValueError("Agent did not produce a response")

        if not report:
            try:
                response_text = full_response.strip()
                report_data = json.loads(response_text)
                report = PeerReviewReport(**report_data)
                logger.info("Successfully parsed PeerReviewReport from JSON")

            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {e}")
                logger.debug(f"Raw response: {full_response}")
                raise ValueError(f"Agent response was not valid JSON: {e}")
            except Exception as e:
                logger.error(f"Error processing review report: {e}")
                raise

            await asyncio.to_thread(
                memory_manager.store_review, blog_id, content, report
            )
            logger.info(f"Stored review in memory for blog_id: {blog_id}")

        return report

    class PeerReviewer:
        @staticmethod
        def review_blog(blog_id: str, content: str) -> PeerReviewReport:
            """
            Synchronous convenience method that internally uses asyncio.run.
            For async applications, prefer using run_peer_review_async directly.
            """
            logger.info(f"Using synchronous wrapper for blog_id: {blog_id}")
            return asyncio.run(run_peer_review_async(blog_id, content))

    peer_reviewer = PeerReviewer()

except Exception as e:
    st.error(f"System Initialization Error: {e}")
    logger.critical(f"Failed to initialize managers in app: {e}")
    st.stop()

st.set_page_config(page_title="Peer Review Agent", layout="wide")


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
                    try:
                        generate_pdf(report, tmp_file.name)
                        with open(tmp_file.name, "rb") as f:
                            st.download_button(
                                label="Download PDF Report",
                                data=f,
                                file_name=f"review_report_{blog_id}.pdf",
                                mime="application/pdf",
                            )
                        os.unlink(tmp_file.name)
                    except Exception as e:
                        st.error(f"Failed to generate PDF: {e}")
                        logger.error(f"PDF generation failed in app: {e}")

                logger.info("Review cycle completed successfully")

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
                logger.error(f"Review process failed: {e}")


if __name__ == "__main__":
    main()
