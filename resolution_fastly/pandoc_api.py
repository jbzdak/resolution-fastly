# coding=utf8

import io
import typing

import requests
import shutil


class PandocException(Exception):
    pass


class PandocApi(object):

    def __init__(self, base_path: str):
        self.base_path = base_path.rstrip('/')

    def convert_url(self, output_format: str, input_format: str):
        return f"{self.base_path}/v0/convert/{input_format}/{output_format}"

    def convert_document(
        self,
        doc_input: typing.Union[io.BytesIO, str],
        doc_output: io.BytesIO,
        output_format: str = "latex",
        input_format: str = "markdown_strict"
    ):

        if isinstance(doc_input, str):
            doc_input = io.BytesIO(doc_input.encode("utf-8"))

        response = requests.post(
            self.convert_url(output_format, input_format),
            data=doc_input,
            stream=True
        )

        if response.status_code != 200:
            raise PandocException()

        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, doc_output)

    def convert_document_to_buffer(
        self,
        doc_input: io.BytesIO,
        output_format: str = "latex",
        input_format: str = "markdown_strict"
    ) -> io.BytesIO:

        output = io.BytesIO()

        self.convert_document(doc_input, output, output_format, input_format)

        output.seek(0)

        return output
