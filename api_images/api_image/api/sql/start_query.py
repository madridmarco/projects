from os import path

def read_query(name_file):
    with open(path.join('api','sql','files_sql',name_file)) as f:
        return f.read()
    
