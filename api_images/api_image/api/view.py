import base64
from api.controller import UserController
from api.models import GetData
from datetime import datetime as dt
from api.utils.response_user import response_user_metod_post
from flask import (
    request, 
    make_response,
    Blueprint
)
bp = Blueprint('picture', __name__, url_prefix='/')

@bp.post('/picture')
def post_image():
    models = UserController()
    data = GetData()

    imgtext = request.json['data']
    imb64 = base64.b64decode(imgtext)
    date = dt.now().strftime('%Y-%m-%d %H:%M:%S')

    min_confianse = request.args.get('min_confianse')
    min_confianse = min_confianse if min_confianse else 80

    pictures = data.info_picture(imgtext= imgtext, imgb64= imb64,date= date)
    data.insert_values(
        name_table = 'pictures', 
        values = pictures
    )

    filter_tags, tags_confidense = models.filter_tags_for_confianse(imgtext=imgtext, min_confianse = min_confianse, date= date)
    data.insert_values(
        name_table = 'tags', 
        values = filter_tags
    )

    return response_user_metod_post(
        imb64 = imb64,
        imgtext = imgtext,
        tags= tags_confidense
    )

@bp.get('/images')
def get_images():
    models = UserController()
    data = GetData()

    min_date = request.args.get("min_date")
    max_date = request.args.get("max_date")

    tags = request.args.get("tags")

    if not min_date and not max_date:
        return make_response('This endpoint needs a date filter in the format YYYY-MM-DD HH:MM:SS', 400)
    
    if min_date and max_date:
        if not models.check_format_date(min_date,max_date):
            return make_response('There are dates that are not in the format YYYY-MM-DD HH:MM:SS', 400)
        filter_date = f"between {min_date} and {max_date}"

    if min_date:
        if not models.check_format_date(min_date):
            return make_response('There are dates that are not in the format YYYY-MM-DD HH:MM:SS', 400)
        filter_date = f">= '{min_date}'"

    if max_date:
        if not models.check_format_date(max_date):
            return make_response('There are dates that are not in the format YYYY-MM-DD HH:MM:SS', 400)
        filter_date = f"<= '{max_date}'"

    return data.end_point_query_param(
        date=filter_date,
        tags = models.if_query_param_tags_is_true(tags)
    )

@bp.get('/image/<id>')
def get_image(id):
    data = GetData()
    return data.end_point_path_parameter(id = id)