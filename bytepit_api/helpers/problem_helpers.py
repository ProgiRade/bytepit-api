import uuid
import re

from typing import List
from fastapi import HTTPException, UploadFile, status

from bytepit_api.database import problem_queries
from bytepit_api.helpers import blob_storage_helpers
from bytepit_api.models.dtos import ModifyProblemDTO


def get_problem(problem_id: uuid.UUID):
    result = problem_queries.get_problem(problem_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Problem with id {problem_id} not found")
    return result


def validate_problems(files: List[UploadFile]):
    if len(files) % 2 == 1 or len(files) == 0:
        return False
    pattern = re.compile(r"^(\d+)_(in|out)\.txt$")
    file_names = set()
    for file in files:
        if not pattern.match(file.filename):
            return False
        if file.filename in file_names:
            return False
        file_names.add(file.filename)
    for i in range(1, (len(file_names) // 2) + 1):
        if f"{i}_in.txt" not in file_names or f"{i}_out.txt" not in file_names:
            return False
    return True


def modify_problem_in_database(problem_id: uuid.UUID, new_problem: ModifyProblemDTO):
    existing_problem = get_problem(problem_id)
    modified_fields = new_problem.model_dump(exclude_none=True, exclude={"test_files"})
    modified_object = existing_problem.model_copy(update=modified_fields)
    result = problem_queries.modify_problem(problem_id, modified_object)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Could not modify problem in database"
        )


def modify_problem_in_blob_storage(problem_id: uuid.UUID, test_files: List[UploadFile]):
    blob_storage_helpers.delete_all_blobs(problem_id)
    for test_file in test_files:
        data = test_file.file.read()
        blob_storage_helpers.upload_blob(f"{problem_id}/{test_file.filename}", data)
