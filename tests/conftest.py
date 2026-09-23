import pytest
import pymupdf


@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "sample.pdf"

    document = pymupdf.open()
    page = document.new_page()
    page.insert_text((72, 72), "Test PDF document")
    document.save(pdf_path)
    document.close()

    return str(pdf_path)
