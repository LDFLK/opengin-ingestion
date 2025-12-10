import os
import json
import logging
from pypdf import PdfReader, PdfWriter
from app.services.gemini import extract_data_with_gemini
from app.schema import parse_extraction_response

logger = logging.getLogger(__name__)

class Agent1:
    """
    The Scanner Agent.
    Responsible for splitting documents and extracting data per page.
    """
    def __init__(self, fs_manager):
        self.fs_manager = fs_manager

    def run(self, pipeline_name: str, prompt: str):
        logger.info(f"Agent 1: Starting scanning for '{pipeline_name}'")
        metadata = self.fs_manager.load_metadata(pipeline_name)
        input_path = metadata.get("input_file")
        
        if not input_path or not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")
            
        # Split PDF
        pages_dir = os.path.join(self.fs_manager._get_pipeline_path(pipeline_name), "input", "pages")
        os.makedirs(pages_dir, exist_ok=True)
        
        page_files = self._split_pdf(input_path, pages_dir)
        
        # Update metadata with page count
        metadata["page_count"] = len(page_files)
        self.fs_manager.save_metadata(pipeline_name, metadata)
        
        # Extract Data for each page
        for i, page_path in enumerate(page_files):
            page_num = i + 1
            logger.info(f"Agent 1: Processing page {page_num}/{len(page_files)}")
            
            try:
                # Call Gemini
                raw_response = extract_data_with_gemini(page_path, prompt)
                
                # Parse to ensure valid structure
                # We reuse the schema logic to get the objects, then serialize back to dict for storage
                parsed_result = parse_extraction_response(raw_response)
                
                page_data = {
                    "page_num": page_num,
                    "tables": [
                        {
                            "id": t.id,
                            "name": t.name,
                            "columns": t.columns,
                            "rows": t.rows
                        } 
                        for t in parsed_result.tables
                    ],
                    "raw_response": parsed_result.raw_response,
                    "message": parsed_result.message
                }
                
                self.fs_manager.save_intermediate_result(pipeline_name, page_num, page_data)
                
            except Exception as e:
                logger.error(f"Agent 1: Failed on page {page_num} - {e}")
                # Save error state for this page?
                self.fs_manager.save_intermediate_result(pipeline_name, page_num, {"error": str(e)})

        logger.info(f"Agent 1: Completed scanning for '{pipeline_name}'")

    def _split_pdf(self, input_path: str, output_dir: str) -> list[str]:
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
