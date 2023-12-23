from nanoid import generate
from typing import Annotated
from fastapi import FastAPI, File, Form, UploadFile, HTTPException, status, Path
from fastapi.responses import FileResponse
from os import getcwd, remove, path

UPLOADS_DIR = getcwd() + "/uploads/"
BASE_URL = "http://127.0.0.1:8000/files/"

app = FastAPI()


@app.post("/files/upload/", status_code=status.HTTP_201_CREATED)
async def create_file(file: Annotated[UploadFile, File()]):
    try:
        ext_file = file.filename.split(".")[1]
        filename_server = f"{generate(size=10)}.{ext_file}"

        with open(UPLOADS_DIR + filename_server, "wb") as myfile:
            content = await file.read()
            myfile.write(content)

        return {
            "filename_server": filename_server,
            "url": BASE_URL + filename_server
        }
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get("/files/{filename_server}")
async def get_file(filename_server: Annotated[str, Path(title="file name on server")]):
    file_path = UPLOADS_DIR + filename_server

    if not path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(file_path)


@app.get("/files/download/{filename_server}")
def download_file(filename_server: Annotated[str, Path(title="file name on server")]):
    file_path = UPLOADS_DIR + filename_server

    if not path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    return FileResponse(file_path, media_type="application/octet-stream", filename=filename_server)


@app.delete("/files/delete/{filename_server}")
async def delete_file(filename_server: Annotated[str, Path(title="file name on server")]):
    try:
        file_path = UPLOADS_DIR + filename_server
        remove(file_path)

        return {"delete": True}
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
