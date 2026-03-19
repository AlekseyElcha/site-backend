import asyncio
import uuid
from typing import List


import boto3
from fastapi import APIRouter, UploadFile, File
from fastapi.params import Path

from src.services.randomizer import generate_random_number_str

s3 = boto3.client(
   service_name='s3',
   endpoint_url='https://s3.ru-7.storage.selcloud.ru',
   verify=False,
   use_ssl=True,
)
bucket_name = "site-backend-s3-bucket"

router = APIRouter(
    prefix="/files",
    tags=["files"],
)

async def upload_single_file(file: UploadFile):
    content = await file.read()
    if len(content) > 25 * 1024 * 1024:
        return {
            "success": False,
            "filename": file.filename,
            "message": "Объём превышает допустимый."
        }
    # file_uuid = uuid.uuid4()

    s3.put_object(
        Bucket=bucket_name,
        Body=content,
        Key=file.filename,
        ContentType=file.content_type or 'application/octet-stream',
    )
    await file.close()
    return {
        "success": True,
        "filename": file.filename,
        "message": "Файл успешно загружен.",
    }


async def upload_multiple_files(
        question_uuid: str,
        files: List[UploadFile] = File(),
):

    filenames = []
    for file in files:
        filenames.append(file.filename)

    results = await asyncio.gather(*[upload_single_file(file) for file in files])

    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    return {
        "message": f"Загружено {len(successful)} из {len(files)} файлов",
        "uploaded": successful,
        "failed": failed if failed else None,
        "file_names": filenames,
    }
