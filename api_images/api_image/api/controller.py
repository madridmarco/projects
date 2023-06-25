from api.models import GetData
import uuid
import re
import pandas as pd

class UserController(GetData):

    def __init__(self):
        super().__init__()


    def filter_tags_for_confianse(self,imgtext,min_confianse, date):

        table_tags =  [
            {
                "tag": t["tag"]["en"],
                "picture_id": str(uuid.uuid5(uuid.UUID('00000000-0000-0000-0000-000000000000'), imgtext)),
                "confidence": t["confidence"],
                "date": date
            }
            for t in self.get_tags(imgtext = imgtext)
            if t["confidence"] > int(min_confianse)
        ]

        if len(table_tags):
            df = pd.DataFrame(table_tags)
            df = (
                df.assign(
                    tags = df.apply(
                        lambda row: {'tag': row['tag'], 'confidence': row['confidence']}, 
                        axis=1
                    )
                )
                [['tags']]
            )
            return table_tags, df.tags.to_list()
        return table_tags, []
    
    @staticmethod
    def check_format_date(*dates):
        pattern = r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$'
        return all(re.match(pattern, date) for date in dates)

    @staticmethod
    def if_query_param_tags_is_true(tags):
        if tags:
            list_tags = ''.join([f"'{j}'"  if i == 0 else f",'{j}'"for i, j in enumerate(tags.split(','))])
            return f"and tag in ({list_tags})"
        return ''