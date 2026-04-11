import asyncio
from typing import List, Annotated

import boto3
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.params import Depends, Body
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from exceptions import S3GetAllFilesError, BasicOperationDatabaseError
from src.config.settings import settings
from src.database.db import get_session
from src.models.models import Questions, Answers

s3 = boto3.client(
   service_name='s3',
   endpoint_url=settings.s3.endpoint,
   verify=False,
   use_ssl=True,
)
bucket_name = settings.s3.container

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


def list_all_files_in_s3():
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
            filenames.append(file.get("key"))
    return filenames


def find_names_for_single_file(
        question_uuid: str,
):
    files_list = list_all_files_in_s3()
    for file in files_list:
        if question_uuid in str(file["key"]):
            return file.get("key")
    return None


async def get_filenames_by_question_id_question(question_id: str, session: AsyncSession):
    query = select(func.unnest(Questions.files)).where(Questions.id == question_id)
    try:
        results = await session.execute(query)
        filenames = results.scalars().all()
        return filenames
    except:
        raise BasicOperationDatabaseError


async def get_filenames_by_question_id_answer(question_id: str, session: AsyncSession):
    query = select(func.unnest(Answers.files)).where(Answers.question_id == question_id)
    try:
        results = await session.execute(query)
        filenames = results.scalars().all()
        return filenames
    except:
        raise BasicOperationDatabaseError


@router.put("/download_all_files_for_question/{question_uuid}")
async def download_multiple_files(
        question_uuid: str,
        session: Annotated[AsyncSession, Depends(get_session)],
):
    # filenames = find_names_for_multiple_files(question_uuid)
    # if not filenames:
    #     raise HTTPException(
    #         status.HTTP_404_NOT_FOUND,
    #         detail="Файлы не были найдены."
    #     )
    filenames = await get_filenames_by_question_id_question(question_uuid, session)
    urls = []
    for filename in filenames:
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": settings.s3.container, "Key": filename},
            ExpiresIn=settings.s3.url_expiration,
        )
        urls.append(url)
    return urls


@router.put("/download_all_files_for_answer/{question_uuid}")
async def download_multiple_files(
        question_uuid: str,
        session: Annotated[AsyncSession, Depends(get_session)],
):
    # filenames = find_names_for_multiple_files(question_uuid)
    # if not filenames:
    #     raise HTTPException(
    #         status.HTTP_404_NOT_FOUND,
    #         detail="Файлы не были найдены."
    #     )
    filenames = await get_filenames_by_question_id_answer(question_uuid, session)
    urls = []
    for filename in filenames:
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": settings.s3.container, "Key": filename},
            ExpiresIn=settings.s3.url_expiration,
        )
        urls.append(url)
    return urls


@router.put("/download_file_by_name")
async def download_file_by_name(file_name: str = Body(embed=True)):
    try:
        url = s3.generate_presigned_url(
            ClientMethod="get_object",
            Params={"Bucket": settings.s3.container, "Key": file_name},
            ExpiresIn=settings.s3.url_expiration,
        )
    except:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            detail="Файл не найден."
        )
    return url
