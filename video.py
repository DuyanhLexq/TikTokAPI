
import requests.cookies
import os
import sys
import requests
import json
import yaml
from .tikheaders import get_headers, download_orginal_video_header
from .comment import commentData,get_comments
from copy import deepcopy
from random import randint

def get_original_video_header(url: str, cookies: requests.cookies.RequestsCookieJar, user_cookie: str) -> dict:
    """
    Generates the headers required for downloading the original video.

    :param url: The URL of the TikTok video.
    :param cookies: The cookies from the initial request to the TikTok page.
    :param user_cookie: The user's cookie string.
    :return: A dictionary containing the headers for downloading the video.
    """

    _header = deepcopy(download_orginal_video_header)
    
    try:
        # Generate a new cookie string from the provided cookies and user_cookie
        new_cookies = []
        cookies = cookies.get_dict()
        user_cookie = user_cookie.replace(" ", "").split(";")

        for raw_cookie in user_cookie:
            first, _ = raw_cookie.split("=", maxsplit=1)
            if not cookies.get(first, False):
                new_cookies.append(raw_cookie)
            else:
                new_cookies.append(f"{first}={cookies[first]}")

        new_cookies = ";".join(new_cookies)
        
        # Update the header with new cookie
        _header["cookie"] = new_cookies

    except Exception as e:
        # Handle unexpected errors during header generation
        print(f"An error occurred while generating headers: {e}")
        raise Exception("Failed to generate headers for the video download") from e

    return _header


def download_file(url: str, header: dict, file_path: str) -> bool:
    """
    Downloads a file from a given URL and saves it locally.

    :param url: The direct URL to the file that needs to be downloaded.
    :param header: The headers required for making the request.
    :param file_path: The local file path where the downloaded file will be saved.
    :return: True if the download is successful, False otherwise.
    """

    try:
        # Attempt to download the file with the provided headers
        response = requests.get(url, stream=True, headers=header)
        if response.ok:
            # Open file to write the video data
            with open(file_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
            return True
        
        else:
            print(f"Failed to download file: HTTP status code {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        # Handle request-specific errors
        print(f"Request failed: {e}")
        return False
    
    except Exception as e:
        # Handle any unexpected errors during download
        print(f"An unexpected error occurred while downloading: {e}")
        return False


def get_all_data_from_url(page_content: str) -> dict:
    """
    Extracts and parses JSON data embedded in the page content.

    :param page_content: The HTML content of the TikTok video page.
    :return: A dictionary containing the extracted data.
    """

    try:
        # Extract JSON data embedded in the page content
        data = page_content[page_content.find('"webapp.video-detail":'):]
        data = data[data.find('"webapp.video-detail":'):data.find("</script>")].replace('"webapp.video-detail":', '')
        
        # Attempt to parse the extracted JSON data
        while len(data) > 0:
            try:
                data = json.loads(data)
                break
            except:
                data = data[:-1]
                
    except Exception as e:
        # Handle unexpected errors during data extraction
        print(f"An error occurred while extracting data: {e}")
        raise Exception("Failed to extract data from page content") from e

    return data


def download_original_video(url: str, local_path=None) -> bool:
    """
    Downloads the original video from TikTok.

    :param url: The URL of the TikTok video.
    :param local_path: The local path where the video will be saved. If None, saves to the script's directory.
    :return: True if the download is successful, False otherwise.
    """

    _headers = deepcopy(get_headers)
    
    try:
        
        # Make a request to the TikTok video page to get its content
        response = requests.get(url, headers=_headers)
        data = get_all_data_from_url(response.text)

        # Get the video ID
        vid_id = data["itemInfo"]["itemStruct"]["id"]
        
        # Handle the local path where the video will be saved
        if local_path is None:
            local_path = os.path.dirname(os.path.abspath(sys.argv[0]))

        FILE_NAME = f"tiktok_vid_{vid_id}.mp4"
        file_path = os.path.join(local_path, FILE_NAME)
        
        try:
            # Get the download URL from the video data
            download_url: str = data["itemInfo"]["itemStruct"]["video"]["playAddr"]
            if not download_url:
                raise ValueError("Download URL not found for the specified video ID")
        
        except KeyError as key_err:
            # Handle missing keys in the JSON data
            print(f"Error retrieving video download information: {key_err}")
            raise Exception("Failed to find necessary keys in data structure") from key_err
        
        except ValueError as val_err:
            # Handle cases where expected values are missing
            print(f"Value error: {val_err}")
            raise Exception("An expected value was not found in the data") from val_err
        
        # Attempt to download the video file
        download_file(download_url, get_original_video_header(download_url, response.cookies, get_headers["cookie"]), file_path)
    
    except Exception as e:
        # Handle unexpected errors during the download process
        print(f"An error occurred while downloading the video: {e}")
        return False
    
    return True


class video_details:
    """
    Some information about the given video.
    """
    def __init__(self,*args):
        self.video_id: str
        self.description: str
        self.hastag: list[dict]
        self.duration: int
        self.width: float | int
        self.height: float | int
        self.diggCount: int
        self.shareCount: int
        self.commentCount: int
        self.playCount: int
        self.collectCount: int
        self.region: str

        # About author
        self.author_id: str
        self.author_uniqueId: str
        self.author_nickname: str
    
    def get_all(self)-> dict:
        return self.__dict__
     
    @staticmethod
    def extract_data_from_path(data: dict, path: str) -> any:
        """
        Extracts data from a nested dictionary using a specified path.

        :param data: The dictionary containing the data.
        :param path: The path to the data in the dictionary.
        :return: The extracted data.
        """
        try:
            key = "/"
            temp = list(map(
                lambda value: f'["{ value}"]',
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
    

def get_video_details(url: str) -> video_details:
    """
    Retrieves details about a TikTok video and its author.

    :param url: The URL of the TikTok video.
    :return: An instance of the `video_details` class containing the details of the video.
    """
    
    try:
        # Get data
        _headers = deepcopy(get_headers)
        
        
        # Make a request to the TikTok video page to get its content
        response = requests.get(url, headers=_headers)
        data = get_all_data_from_url(response.text)

        with open(f"{os.path.dirname(__file__)}/yaml/video_details_path.yaml", 'r') as file:
            paths: dict = yaml.safe_load(file)

        video_details_ = video_details()
        for key, value in paths.items():
            video_details_.__setattr__(key, video_details.extract_data_from_path(data, value))

    except KeyError as key_err:
        print(f"Error extracting video details: {key_err}")
        raise Exception("Failed to find necessary keys in data structure") from key_err
    
    except FileNotFoundError as fnf_err:
        print(f"File not found: {fnf_err}")
        raise Exception("Required file for extracting video details was not found") from fnf_err

    except Exception as e:
        print(f"An unexpected error occurred while retrieving video details: {e}")
        raise Exception("Failed to retrieve video details") from e

    return video_details_





    
    

