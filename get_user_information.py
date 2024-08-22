import requests
import os
import json
import yaml
from .tikheaders import get_headers
from typing import Optional
from copy import deepcopy

class user_information:
    """
    Basic information about the author
    """
    def __init__(self, *args):
        self.id: str
        self.uniqueId: str
        self.nickname: str
        self.description: str
        self.createTime: int
        self.nickNameModifyTime: int
        self.verified: bool
        self.secret: bool
        self.privateAccount: bool
        self.followerCount: int
        self.followingCount: int
        self.heartCount: int
        self.videoCount: int
        self.diggCount: int
        self.friendCount: int
        self.language: str
        self.region: str
    
    def __repr__(self)-> str:
        try:
            info = f"<user_information (id={self.id},followers={self.followerCount},hearts={self.heartCount},...)>"
        except:
            info = f"<user_information ()>"
        return info
    
    def __getitem__(self,name:str):
        try:
            return self.__getattribute__(name)
        except:
            return None
    
    def get_all(self):
        return self.__dict__
    


    @staticmethod
    def extract_data_from_path(data: dict, path: str) -> Optional[any]:
        """
        Extracts data from a nested dictionary using a specified path.

        :param data: The dictionary containing the data.
        :param path: The path to the data in the dictionary.
        :return: The extracted data.
        :raises KeyError: If the specified path is not found in the data.
        :raises Exception: If an unexpected error occurs during data extraction.
        """
        try:
            key = "/"
            temp = list(map(
                lambda value: f'["{value}"]',
                path.split(key)
            ))
            new_path = ""
            for val in temp:
                new_path += val

        except KeyError as e:
            raise KeyError("Cannot find the path in the data structure") from e
        
        except Exception as e:
            print(f"An unexpected error occurred while extracting data: {e}")
            raise Exception("Failed to extract data from path") from e
        
        return eval(f"data{new_path}")


def get_user_info(url: str) -> user_information:
    """
    Retrieves detailed information about a TikTok user.

    :param url: The URL of the TikTok user profile.
    :return: An instance of the `user_information` class containing the user's details.
    :raises FileNotFoundError: If the path to the JSON configuration file is not found.
    :raises KeyError: If required keys are missing in the JSON data.
    :raises Exception: If an unexpected error occurs during the process.
    """
    try:
        _headers = deepcopy(get_headers)

        # Make a request to the TikTok user page to get its content
        response = requests.get(url, headers=_headers)
        page_content = response.text

        # Extract JSON data embedded in the page content
        data = page_content[page_content.find('"webapp.user-detail":'):]
        data = data[data.find('"webapp.user-detail":'):data.find("</script>")].replace('"webapp.user-detail":', '')
        
        # Attempt to parse the extracted JSON data
        while len(data) > 0:
            try:
                data = json.loads(data)
                break
            except:
                data = data[:-1]

        # Load the paths configuration file
        with open(f"{os.path.dirname(__file__)}/yaml/user_info_path.yaml", 'r') as file:
            paths: dict = yaml.safe_load(file)

        user_info = user_information()
        for key, value in paths.items():
            user_info.__setattr__(key, user_information.extract_data_from_path(data, value))

    except FileNotFoundError as fnf_err:
        print(f"File not found: {fnf_err}")
        raise Exception("Required file for extracting user details was not found") from fnf_err
    
    except KeyError as key_err:
        print(f"Error extracting user details: {key_err}")
        raise Exception("Failed to find necessary keys in data structure") from key_err

    except Exception as e:
        print(f"An unexpected error occurred while retrieving user details: {e}")
        raise Exception("Failed to retrieve user details") from e

    return user_info

