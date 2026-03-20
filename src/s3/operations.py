import asyncio
import uuid
from typing import List, Dict, Any

import boto3
from fastapi import APIRouter, UploadFile, File
from fastapi.params import Path, Depends, Body

from exeptions import S3GetAllFilesError
from src.config.settings import settings
from src.services.randomizer import generate_random_number_str

s3 = boto3.client(
   service_name='s3',
   endpoint_url=settings.s3.endpoint,
   verify=False,
   use_ssl=True,
)
bucket_name = settings.s3.bucket_name

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


def list_all_files_in_s3() -> dict:
    prefix = ""
    objects = []
    try:
        paginator = s3.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix=prefix):
            if "Contents" in page:
                for obj in page["Contents"]:
                    objects.append(
                        {
                            "key": obj["Key"],
                            "size": obj["Size"],
                            "last_modified": obj["LastModified"],
                            "etag": obj["ETag"],
                        }
                    )

        return objects
    except:
        raise S3GetAllFilesError

# print(list_all_files_in_s3())

def find_names_for_multiple_files(
        question_uuid: str,
):
    files_list = list_all_files_in_s3()
    filenames = []
    for file in files_list:
        if question_uuid in str(file["key"]):
            filenames.append(file)
    return filenames


# @router.put("/download_files/{question_uuid}")
# async def download_multiple_files(question_uuid: str = Body(embed=True)):
#     filenames = find_names_for_multiple_files(question_uuid)
#     url = s3.generate_presigned_url(
#         ClientMethod="get_object",
#         Params={"Bucket": settings., "Key": OBJECT_KEY},
#         ExpiresIn=EXPIRES_IN,
#     )
#     return 1
