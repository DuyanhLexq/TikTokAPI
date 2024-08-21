from re import findall

def get_video_id(url:str)-> str:
    url_end = url.split("/")[-1]
    return findall(r'[0-9]{4,}',url_end)[0]
