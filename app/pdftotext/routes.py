from http import HTTPStatus

from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse

from .processor import converter

__all__ = ['router']

router = APIRouter(
    prefix="/pdftotext",
)


@router.get('/')
async def get_pdf_to_text_page():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF to Text Converter</title>
        <style>
            body { display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; font-family: Arial, sans-serif; }
            .container { text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PDF to Text Converter</h1>
            <form action="/v1/pdftotext" method="post" enctype="multipart/form-data">
                <input type="file" name="pdf_file" accept=".pdf" required>
                <button type="submit">Convert</button>
            </form>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.post('/')
async def convert_pdf_to_text(request: Request, pdf_file: UploadFile = File(...)):
    job_id = converter.submit(await pdf_file.read())
    return RedirectResponse(
        url=f"{request.url_for('get_job_status', job_id=job_id)}",
        status_code=HTTPStatus.SEE_OTHER
    )


@router.get('/{job_id}')
async def get_job_status(job_id: str):
    try:
        text = converter.check(job_id)
        if text is not None:
            return PlainTextResponse(text)
    except KeyError as e:
        raise HTTPException(status_code=404, detail="Job not found")

    html_content = f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PDF to Text Conversion Status</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
            }}
            .container {{
                text-align: center;
            }}
            h1 {{
                margin-bottom: 0.5rem;
            }}
            #status {{
                font-size: 1.1rem;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>PDF to Text Conversion</h1>
            <div id="status">Conversion in progress. Please wait...</div>
        </div>
        <script>
            setTimeout(function() {{
                window.location.reload(1);
            }}, 5000); // Reload every 5 seconds
        </script>
    </body>
    </html>
    '''
    return HTMLResponse(content=html_content)
