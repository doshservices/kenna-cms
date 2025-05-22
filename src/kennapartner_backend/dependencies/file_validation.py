from fastapi import UploadFile, HTTPException


"""
A class to validate uploaded files in a FastAPI application.

Attributes:
    file (UploadFile): The uploaded file to be validated.

Methods:
    check_file_type(): Validates the file type against allowed content types.
    check_file_size(): Validates the file size against the allowed limit.
"""
class FileValidator:
    def __init__(self, file: UploadFile):
        self.file = file
        self.check_file_type()
        self.check_file_size()

    def check_file_type(self):
        allowed_content_type = ["image/jpeg", "image/png"]
        if self.file.content_type not in allowed_content_type:
            raise HTTPException(
                status_code=400, detail={"message": "File type not allowed"}
            )
        else:
            return True

    def check_file_size(self):
        allowed_file_size = 2 * 1024 * 1024  # 2mb

        self.file.file.seek(0)
        if len(self.file.file.read()) > allowed_file_size:
            raise HTTPException(
                status_code=400, detail={"message": "File size excedeed 2mb"}
            )
        else:
            return True
