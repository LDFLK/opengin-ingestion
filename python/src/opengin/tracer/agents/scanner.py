import logging
import os

from pypdf import PdfReader, PdfWriter

from opengin.tracer.schema import parse_extraction_response
from opengin.tracer.services.gemini import extract_data_with_gemini

logger = logging.getLogger(__name__)


class Agent1:
    """
    The Scanner Agent (Agent 1).

    This agent is responsible for the initial processing of the input document.
    Its primary tasks are:
    1. Splitting the input PDF into individual pages.
    2. Sending each page to the GenAI service (Gemini) for data extraction based on the prompt.
    3. Saving the raw and parsed extraction results to the 'intermediate' directory.
    """

    def __init__(self, fs_manager):
        """
        Initialize the Scanner Agent.

        Args:
            fs_manager (FileSystemManager): Instance for handling file operations.
        """
        self.fs_manager = fs_manager

    def run(self, pipeline_name: str, run_id: str, prompt: str):
        """
        Executes the scanning and extraction phase.

        Iterates through each page of the split PDF and performs extraction.

        Args:
            pipeline_name (str): The name of the pipeline.
            run_id (str): The unique identifier for the run.
            prompt (str): The extraction prompt to send to the LLM.

        Raises:
            FileNotFoundError: If the input file recorded in metadata does not exist.
        """
        logger.info(f"Agent 1: Starting scanning for '{pipeline_name}' run '{run_id}'")
        metadata = self.fs_manager.load_metadata(pipeline_name, run_id)
        input_path = metadata.get("input_file")

        if not input_path or not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Split PDF
        pages_dir = self.fs_manager.get_input_pages_dir(pipeline_name, run_id)
        os.makedirs(pages_dir, exist_ok=True)

        page_files = self._split_pdf(input_path, pages_dir)

        # Update metadata with page count
        metadata["page_count"] = len(page_files)
        self.fs_manager.save_metadata(pipeline_name, run_id, metadata)

        # Extract Data for each page
        for i, page_path in enumerate(page_files):
            page_num = i + 1
            logger.info(f"Agent 1: Processing page {page_num}/{len(page_files)}")

            try:
                # Call Gemini
                raw_response = extract_data_with_gemini(page_path, prompt)

                # Parse to ensure valid structure
                parsed_result = parse_extraction_response(raw_response)

                tables_data = []
                for t in parsed_result.tables:
                    tables_data.append(
                        {
                            "id": t.id,
                            "name": t.name,
                            "columns": t.columns,
                            "rows": t.rows,
                        }
                    )

                page_data = {
                    "page_num": page_num,
                    "tables": tables_data,
                    "raw_response": parsed_result.raw_response,
                    "message": parsed_result.message,
                }

                self.fs_manager.save_intermediate_result(pipeline_name, run_id, page_num, page_data)

            except Exception as e:
                logger.error(f"Agent 1: Failed on page {page_num} - {e}")
                self.fs_manager.save_intermediate_result(pipeline_name, run_id, page_num, {"error": str(e)})

        logger.info(f"Agent 1: Completed scanning for '{pipeline_name}'")

    def _split_pdf(self, input_path: str, output_dir: str) -> list[str]:
        """
        Splits a multipage PDF into individual single-page PDFs.

        Args:
            input_path (str): Path to the source PDF.
            output_dir (str): Directory to save the split pages.

        Returns:
            list[str]: A list of file paths for the generated single-page PDFs.
        """
        reader = PdfReader(input_path)
        page_files = []

        for i, page in enumerate(reader.pages):
            writer = PdfWriter()
            writer.add_page(page)

            output_filename = f"page_{i+1}.pdf"
            output_path = os.path.join(output_dir, output_filename)

            with open(output_path, "wb") as f:
                writer.write(f)

            page_files.append(output_path)

        return page_files
