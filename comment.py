import requests
import os
import yaml
from typing import Self
from random import randint

class commentData:
    """
    The data structure of comments.

    Base on Link-list principle.
    """
    def __init__(self):
        self.author_pin:str
        self.aweme_id:str
        self.cid:str
        self.collect_stat:str
        self.comment_language:str
        self.create_time:int
        self.digg_count:int
        self.reply_comment_total:int
        self.text:str
        self.author_id:str
        self.replies:list[Self] = []

    def __len__(self):
        """
        :return: The number of replies
        """
        return len(self.replies)
    
    def __repr__(self):
        try:
            info = f"<commentData ({self.author_id},{self.text},{self.comment_language})>"
        except:
            info = "<(commentData)>"
        finally:
            return info
    
    def __getitem__(self,name:str)-> any:
        try:
            return self.__getattribute__(name)
        except:
            return None
        
    def get_all(self)-> dict[str:any]:
        return self.__dict__

        
    def append_reply(self,comment:Self)-> None:
        """
        Add reply into the comment data.

        :param: comment: The other data comment class

        """
        if len(self.replies) >= self.reply_comment_total:raise IndexError("The size of replies was over !")
        self.replies.append(comment)
    
    @staticmethod
    def extract_data_from_path(data:dict,path:str)-> any:
        key = "/"
        def convert(value):
            try:
                return f"[{int(value)}]"
            except:
                return f'["{value}"]'

        new_path = ''.join(list(map(
            convert,
            path.split(key)
        )))
    
        return eval("data"+new_path)

def get_replies(video_id: str, comment_id: str, msToken: str, maxcount=20, cursor=0, current_size=0):
    """
    Fetch replies to a specific comment on a TikTok video.

    Args:
        video_id (str): The ID of the video.
        comment_id (str): The ID of the comment to fetch replies for.
        msToken (str): Authentication token required for the request.
        maxcount (int, optional): Maximum number of replies to fetch per request. Defaults to 20.
        cursor (int, optional): Pagination cursor to fetch the next set of replies. Defaults to 0.
        current_size (int, optional): The current count of fetched replies, used for recursion. Defaults to 0.

    Returns:
        list: A list of commentData objects containing the replies.
    """

    from .tikparams import reply_params as params
    from .tikheaders import get_headers as headers

    def fill_params():
        """
        Fill the request parameters with required data such as comment ID, video ID, and device information.
        """
        # Define the required keys and their corresponding values
        keys = [
            "comment_id",      # Comment ID
            "count",           # Number of comments to fetch
            "cursor",          # Cursor for pagination
            "device_id",       # Random device ID
            "item_id",         # Video ID
            "screen_height",   # Random screen height
            "screen_width",    # Random screen width
            "msToken"          # Token for authentication
        ]
        values = [
            comment_id,                         # Use the provided comment_id
            maxcount,                           # Set the max count of comments
            cursor,                             # Set the cursor for pagination
            ''.join(str(randint(1, 9)) for _ in range(19)), # Random device ID with length 19
            video_id,                           # Use the provided video_id
            randint(500, 1000),                 # Random screen height between 500 and 1000
            randint(1000, 1500),                # Random screen width between 1000 and 1500
            msToken                             # Use the provided msToken
        ]
        
        # Populate the params dictionary with the keys and values
        for key, value in zip(keys, values):
            params[key] = value
    
    fill_params()
    data_return = []
    
    try:
        base_url = "https://www.tiktok.com/api/comment/list/reply/"
        response = requests.get(base_url, params=params, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors
        
        data: dict = response.json()

        # Load the paths configuration file to extract data from the JSON response
        with open(f"{os.path.dirname(__file__)}/yaml/comments_path.yaml", 'r') as file:
            paths: dict = yaml.safe_load(file)

        root = "comments"

        # If no comments are found in the response, return an empty list
        if not data.get(root, False):
            return []

        # Loop through the comments and extract the necessary data
        for i in range(len(data[root])):
            obj = commentData()
            for key, value in paths.items():
                try:
                    obj.__setattr__(key, obj.extract_data_from_path(data, f'{root}/{i}/{value}'))
                except:
                    obj.__setattr__(key, None)
            data_return.append(obj)

        # Recursively fetch more comments if they exist
        return data_return + get_replies(video_id, comment_id, msToken, maxcount=maxcount, cursor=cursor + 1, current_size=current_size + len(data_return))

    except requests.exceptions.RequestException as e:
        # Handle any errors related to the request itself
        print(f"Request failed: {e}")
        return []
    
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return []
    
    

def get_comments(url: str, msToken: str, maxcount: int = 20, cursor: int = 0, current_size: int = 0) -> list[commentData]:
    """
    Fetches comments from a TikTok video using the provided URL and msToken.

    :param url: The URL of the TikTok video.
    :param msToken: A token required for authenticating the request.
    :param maxcount: Maximum number of comments to fetch in one request (default: 20).
    :param cursor: The starting point for fetching comments (used for pagination).
    :param current_size: The current number of comments fetched (used for recursion).
    :return: A list of `commentData` objects containing the comments data.
    """
    
    data_return:list[commentData] = []
    
    from .tikparams import comment_params as params
    from .tikheaders import get_headers
    from .functions import get_video_id

    def fill_params():
        """
        Fills the parameters required for making the comments API request.
        """
        # Define the required keys and their corresponding values
        keys = [
            "aweme_id",        # Video ID extracted from the URL
            "count",           # Number of comments to fetch
            "cursor",          # Cursor for pagination
            "device_id",       # Random device ID
            "screen_height",   # Random screen height
            "screen_width",    # Random screen width
            "msToken"          # Token for authentication
        ]
        values = [
            get_video_id(url),                  # Extract video ID from the URL
            maxcount,                           # Set the max count of comments
            cursor,                             # Set the cursor for pagination
            ''.join(str(randint(1, 9)) for _ in range(19)), # Random device ID with length 19
            randint(500, 1000),                 # Random screen height between 500 and 1000
            randint(1000, 1500),                # Random screen width between 1000 and 1500
            msToken                             # Use the provided msToken
        ]
        
        # Populate the params dictionary with the keys and values
        for key, value in zip(keys, values):
            params[key] = value

    # Fill the request parameters
    fill_params()
    #get id video
    video_id = get_video_id(url)

    base_url = "https://www.tiktok.com/api/comment/list/"

    try:
        # Make the request to TikTok's API to get the comments
        response = requests.get(base_url, params=params, headers=get_headers)
        response.raise_for_status()  # Raise an error for bad responses
        data: dict = response.json()

        # Load the paths configuration file to extract data from the JSON response
        with open(f"{os.path.dirname(__file__)}/yaml/comments_path.yaml", 'r') as file:
            paths: dict = yaml.safe_load(file)

        root = "comments"

        # If no comments are found in the response, return an empty list
        if not data.get(root, False):
            return []

        # Loop through the comments and extract the necessary data
        for i in range(len(data[root])):
            obj = commentData()
            for key, value in paths.items():
                obj.__setattr__(key, obj.extract_data_from_path(data, f'{root}/{i}/{value}'))
            data_return.append(obj)

        for i in range(len(data_return)):
            if data_return[i].reply_comment_total < 1:continue
            data_return[i].replies.extend(get_replies(video_id,data_return[i].cid,msToken))


        # Recursively fetch more comments if they exist
        return data_return + get_comments(url, msToken, maxcount, cursor=cursor + 20, current_size=current_size + len(data_return))

    except requests.exceptions.RequestException as e:
        # Handle any errors related to the request itself
        print(f"Request failed: {e}")
        return []
    
    except Exception as e:
        # Handle any other unexpected errors
        print(f"An unexpected error occurred: {e}")
        return []





        

    