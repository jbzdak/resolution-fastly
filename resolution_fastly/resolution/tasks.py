# coding=utf8

from celery import shared_task

import io

from django.conf import settings
from django.core.files import File
from django.template.loader import get_template

from . import models
from resolution_fastly.pandoc_api import PandocApi


pandoc = PandocApi(settings.PANDOC_API_LOCATION)


@shared_task()
def render_resolution(resolution_id: int):

    resolution = models.Resolution.objects.get(pk=resolution_id)
    template = get_template("resolution_template.md")
    markdown = template.render({
        "resolution": resolution
    })
    resolution.save_format(
        "text/markdown",
        io.BytesIO(markdown.encode("utf-8"))
    )
    resolution.save_format(
        "application/pdf",
        pandoc.convert_document_to_buffer(
            doc_input=markdown,
            output_format="latex"
        )
    )
    resolution.save_format(
        "application/pdf",
        pandoc.convert_document_to_buffer(
            doc_input=markdown,
            output_format="docx"
        )
    )


