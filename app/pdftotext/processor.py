import tempfile
import asyncio
from asyncio import Future
from typing import Dict
from uuid import uuid4
from pathlib import Path

from ..foundation import pdf


class PdfToTxtConverter(object):

    def __init__(self):
        self._jobs: Dict[str, Future] = {}

    def submit(self, content: bytes) -> str:
        job_id = str(uuid4())
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(None, self.convert, content)
        self._jobs[job_id] = future
        return job_id

    def check(self, job_id: str) -> bool:
        if self._jobs[job_id].done():
            return self._jobs[job_id].result()
        return None

    def convert(self, content: bytes) -> str:
        with tempfile.TemporaryDirectory() as tmpdir:
            pdf_path = Path(tmpdir) / "input.pdf"
            pdf_path.write_bytes(content)
            pdf_flyweight = pdf.PDFlyweight(Path(tmpdir))
            pdf_flyweight.to_pages(str(pdf_path))
            text = pdf_flyweight.to_text()
            return text


converter = PdfToTxtConverter()
