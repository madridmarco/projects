import requests
from sqlalchemy.exc import IntegrityError
import pandas as pd
import uuid
from imagekitio import ImageKit
from PIL import Image
from io import BytesIO
from api.engine.mysql import EngineMySql
from api.data.read_data import credentials
from api.sql.start_query import read_query
import base64

class GetData():
    __enpoint_imagga = 'https://api.imagga.com/v2/tags?image_url'

    def __init__(self):

        self.db = EngineMySql(
            host = 'db',
            user = 'mbit',
            password = 'mbit',
            db = 'pictures',
            autocommit = True
        )

    def insert_values(self, name_table, values):
        try:
            if name_table == 'pictures':
                pd.DataFrame(values).to_sql(name_table, con=self.db.engine_with_url(), if_exists='append', index=False)
            else:
                new_data = pd.DataFrame(values)
                if not new_data.empty:
                    id = new_data.iloc[0]['picture_id']
                    
                    old_data = self.db.run_query(
                        query= f"select * from tags where picture_id = '{id}'",
                        dql = True
                    )

                    if not old_data.empty:
                        append_new_data = new_data[~new_data.isin(old_data)].dropna()
                        if not append_new_data.empty:
                            append_new_data.to_sql(name_table, con=self.db.engine_with_url(), if_exists='append', index=False)

                    new_data.to_sql(name_table, con=self.db.engine_with_url(), if_exists='append', index=False)
        except IntegrityError as e:
            error_message = str(e)
            if '1062' in error_message:
                print(f'Errro prima: El registro ya existe. Detalles: {error_message}')

    def get_tags(self,imgtext):

        imagekit = ImageKit(
            public_key= credentials['Imagekit']['public_key'],
            private_key = credentials['Imagekit']['private_key'],
            url_endpoint = credentials['Imagekit']['url_endpoint']
        )

        upload_info = imagekit.upload(file=imgtext, file_name= "my_file_name.jpg")

        api_key = credentials['imagga']['api_key']
        api_secret = credentials['imagga']['api_secret']

        try:
            response = requests.get(f"{GetData.__enpoint_imagga}={upload_info.url}", auth=(api_key, api_secret))
            imagekit.delete_file(file_id=upload_info.file_id)
            return response.json()["result"]["tags"]
        except Exception as ex:
            raise Exception(f'ERROR in get_tags: {ex}')
           
    def info_picture(self,imgtext,imgb64,date):
        pictures = [
            {
                'id'  : str(uuid.uuid5(uuid.UUID('00000000-0000-0000-0000-000000000000'), imgtext)),
                'path' : self.__save_image(imgtext= imgtext, imgb64= imgb64),
                'date' : date
            }
        ]
        return pictures
    
    def end_point_query_param(self,date,tags):

        query = read_query('get_images.sql')
        query = query.replace('replace_filter_date',date)
        query = query.replace('tags_',tags)
        
        df = self.db.run_query(query = query, dql=True)

        distinct_img = df[['id','path']].drop_duplicates().to_dict(orient='records')
        kb = dict(map(lambda x: (x['id'], self.__info_img(path= x['path'], text= False)),distinct_img))
        
        df = (
            df.assign(
                size=lambda df: df.id.map(
                    lambda x: kb[x]
                ),
                tags=df.apply(
                    lambda row: {'tag': row['tag'], 'confidence': row['confidence']}, 
                    axis=1
                )
            )
            [['id', 'size', 'date', 'tags']]
        )
        
        return df.to_dict(orient='records')

    def end_point_path_parameter(self,id):
        query = read_query('get_image.sql').replace('_id_', f"'{id}'")
        df = self.db.run_query(query = query, dql=True)
        df = (
            df.assign(
                tags=df.apply(
                    lambda row: {'tag': row['tag'], 'confidence': row['confidence']}, 
                    axis=1
                )
            )
        )

        imgtext, size = self.__info_img(path= df.iloc[0]['path'])

        return {
            'id' : id,
            'size' : size,
            'date' : df.iloc[0]['date'],
            'tags' : df.tags.to_list(),
            'data' : imgtext
        }

    def __save_image(self,imgtext,imgb64):
        image = Image.open(BytesIO(imgb64))
        path = f"/app/imagenes/{str(uuid.uuid5(uuid.UUID('00000000-0000-0000-0000-000000000000'), imgtext))}.jpeg"
        image.save(path)
        return path
    
    def __info_img(self,path, text = True, kb = True):

        with open(path, mode="rb") as img:
            img_text = base64.b64encode(img.read()).decode()
        size_img  = len(base64.b64decode(img_text)) /1024

        if text and kb:
            return img_text, size_img
        elif text:
            return img_text
        elif kb:
            return size_img