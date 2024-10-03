import base64
import io
import itertools
import logging
import pathlib
import tempfile
import time
from argparse import ArgumentParser
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import fitz
import openai
from openai.types import chat

__all__ = ["PDFlyweight"]


class PDFlyweight:
    def __init__(self, working_dir: Path | str, vision_model="gpt-4o", text_model="gpt-4o"):
        self._working_dir = None
        self._text_model = text_model
        self._vision_model = vision_model
        self._openai_clients: list[openai.OpenAI] = [
            openai.OpenAI()
        ]
        self.set_work_dir(working_dir)

    def set_work_dir(self, working_dir) -> "PDFlyweight":
        self._working_dir: Path = working_dir if isinstance(working_dir, Path) else Path(str(working_dir))
        self._working_dir.mkdir(exist_ok=True)
        return self

    def __iter__(self):
        return self._working_dir.iterdir()

    def to_pages(self, input_path, fmt="png"):
        """
        Split PDF file into pages and save them as images
        """
        assert input_path.endswith("pdf")
        doc = fitz.open(input_path)

        for num, page in enumerate(doc.pages()):
            page_rect = page.rect
            area = page_rect.get_area()  # number of the pixels at the page.
            dpi = 72  # Default DPI for the PDF.
            if area >= 1366 * 768:
                # Resolution is high. We keep DPI as it is
                dpi = None
            elif 640 * 360 < area < 1366 * 768:
                # Resolution is medium. So we need to bump DPI.
                # PDF is vector format - the output image will be crisp, but embedded images may be slightly blur
                dpi = 72 * 2
            else:
                # Resolution is low. Use even high DPI
                dpi = 72 * 3

            pix: fitz.Pixmap = page.get_pixmap(dpi=dpi)
            pix.save(self._working_dir / f"page_{num + 1:03d}.{fmt}")

    def image_to_text(self, input_image: io.BytesIO, fmt="png") -> str:
        """
        Convert image as a byte array to string with GPT vision and confirmation from the GPT4-Turbo
        """
        base64_image = base64.b64encode(input_image).decode("utf-8")
        openai_client_iterator = itertools.cycle(self._openai_clients)
        messages = [
            {"role": "system", "content": self._get_prompt("extract_text_from_image")},
            {
                "role": "user",
                "content": [{"type": "image_url", "image_url": {"url": f"data:image/{fmt};base64,{base64_image}"}}],
            },
        ]
        contents = []
        for attempt in range(1, 6):
            client = next(openai_client_iterator)
            response: chat.ChatCompletion | None = None
            try:
                response = client.chat.completions.create(
                    model=self._vision_model,
                    messages=messages,
                    temperature=0,
                    max_tokens=4096,
                )
            except openai.RateLimitError as e:
                logging.warning(f"Attempt # {attempt} - rate limit exceeded for API key: {e}")
                time.sleep(1)
                continue  # Skip the rest of the loop and move to the next image
            content_response = response.choices[0].message.content
            contents.append(content_response)
            logging.debug("Verify the output of vision with text model")
            response = client.chat.completions.create(
                model=self._text_model,
                messages=[
                    {"role": "system", "content": self._get_prompt("verify_extracted_text")},
                    {"role": "user", "content": content_response},
                ],
                temperature=0,
                max_tokens=4096,
            )
            judgement = response.choices[0].message.content
            if judgement in {"0", "Response 0"}:
                # Successful response sometime is '0', sometime is "Response 0"
                return content_response
            logging.warning(f"Attempt # {attempt} - hallucinations detected: {judgement}")
        logging.warning(
            f"Failed to recognize image after {attempt} attempts without hallucinations. "
            f"Largest response will be used"
        )
        return max(contents)

    def file_path_to_text(self, file_path: pathlib.Path):
        try:
            name, fmt = file_path.name.split(".")
            page, page_num = name.split("_")
            page_num = int(page_num)
            text = self.image_to_text(file_path.read_bytes(), fmt)
            return "\n\n".join(
                [
                    f"Source: pitch_deck/page={page_num}",
                    text,
                ]
            )
        except ValueError as e:
            logging.error(f"Unexpected file name for the image: {file_path}")
            raise e

    def to_text(self, images: list[Path] = []):
        images = images if images else sorted(self._working_dir.iterdir())

        with ThreadPoolExecutor() as pool:
            tasks = [pool.submit(self.file_path_to_text, path) for path in images if path.name.startswith("page")]
            return "\n=======================================\n".join([task.result() for task in tasks])

    def _get_prompt(self, prompt_id):
        return prompts.get(prompt_id)


prompts = {
    "extract_text_from_image": """
Goal: extract text from the slide presentation in detail, ensuring no loss of meaning.
Requirements:
 * highlight and write the title and subtitle of the slide if they exist. Maintain pagination as in the original.
 * Acknowledge Logos, charts, diagrams and explain their relation to the text.
 * Ignore the logo in the slide needle.
 * Ignore background images.
 * Ignore watermarks and "CONFIDENTIAL" ones on the slides.
 * Write tables from input in markdown format
""",
    "verify_extracted_text": """
Your goal is to control the quality of another machine learning mode. That model converts images to text.
Occasionally, the model does not recognize or refuse to provide details from the image.
Find the text where the model explicitly refuses to provide details from the original image.
Response "0" if everything was recognized otherwise return what was missed.
""",
}


def main(working_dir, input_path):
    logging.info(f"Work in {working_dir} with {input_path}")
    for path in Path(working_dir).iterdir():
        if path.is_file():
            path.unlink(missing_ok=True)

    pdf = PDFlyweight(Path(working_dir))
    pdf.to_pages(input_path)
    logging.info("Images are ready")

    start = time.time()
    text = pdf.to_text()
    end = time.time()
    logging.info(f"New {end-start} sec")


if __name__ == "__main__":
    logging.root.setLevel(logging.INFO)
    argparse = ArgumentParser()
    argparse.add_argument("-f", "--file", help="Input file", required=True)
    argparse.add_argument("-d", "--dir", help="Working dir", default=None)
    args = dict(vars(argparse.parse_args()))
    assert args["file"].endswith("pdf"), "Input file must be valid PDF"

    if args["dir"]:
        main(args["dir"], args["file"])
    else:
        with tempfile.TemporaryDirectory() as tmpdir:
            main(tmpdir, args["file"])
