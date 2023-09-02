from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view

from shared.dtos.ordinary_response_dto import BadRequestDto, InternalServerErrorDto, OkDto
from shared.response.json_response import BadRequestResponse, InternalServerErrorResponse, OkResponse
from shared.utils.file.exceptions import FileException
from shared.utils.file.file_handler import parse_filename
from shared.utils.parameter.parameter import parse_param
from shared.utils.parameter.value_parser import parse_value
from tool.utils.docx_util import prepare_docx_file


# Create your views here.

@api_view(['POST'])
@csrf_exempt
def convert_html_to_docx(request):
    params = parse_param(request)
    filename: str = parse_value(params.get("filename"), str, "Document")
    if not filename.endswith(".docx"):
        filename += ".docx"
    filename, _ = parse_filename(filename)
    html = parse_value(params.get("html"), str)
    if html is None:
        return BadRequestResponse(BadRequestDto("Missing HTML"))

    try:
        url = prepare_docx_file(html, filename)
    except FileException as e:
        return InternalServerErrorResponse(InternalServerErrorDto("Failed to convert HTML to DOCX", data=e))

    return OkResponse(OkDto(data={"url": url}))
