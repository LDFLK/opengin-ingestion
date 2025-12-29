import os

import pytest


@pytest.fixture
def sample_data_dir():
    # Helper to locate the data directory relative to this file
    # tests are in python/integration_tests/
    # data is in repo_root/data/ which is ../../data from here
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "../../data"))


@pytest.fixture
def validation_data_dir():
    return os.path.join(os.path.dirname(__file__), "validation_data")


@pytest.fixture
def metadata_schema():
    return """fields:
  - name: table_name
    description: Name of the table
    type: string
  - name: row_count
    description: Number of rows in the table
    type: integer
"""


@pytest.fixture
def simple_prompt():
    return "Extract all tables from the provided document. Preserve the structure and cell contents."


@pytest.fixture
def advanced_prompt():
    return """**Objective:** Extract all tables from the provided document.

**Instructions:**
1. **Identify Multiple Tables:** The document may contain multiple distinct tables on the same page.
     Identify each table separately.
2. **Table Separation:** Do NOT merge separate tables. Treat them as distinct entities.
3. **Metadata Collection:** Extract metadata for each table as per the provided metadata schema.
4. **Consistency:** Ensure independent extraction for each table found.
"""
