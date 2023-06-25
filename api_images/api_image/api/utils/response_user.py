import uuid

def response_user_metod_post(imb64,imgtext,tags):
    return {
        'id' : str(uuid.uuid5(uuid.UUID('00000000-0000-0000-0000-000000000000'), imgtext)),
        'kb' : len(imb64) / 1024,
        'tags' : tags,
        'data' : imgtext,
    }