# Author: Amelia Wietting
# Date: 20220119

from enum import Enum
import pickle
import json
import os
import subprocess
import shutil
import requests



class apiType(Enum):
    EPICDSCOVR = "epicdscovr"


class projectEarth():
    def __init__(self, product_type=None):
        print("Welcome to Project Earth, starting up...")

        if product_type is None:
            print("Please select a valid api, the following are supported:")
            for item in apiType:
                print(item.name)
            return None

        self.product_type = product_type

        if self.product_type is apiType.EPICDSCOVR:
            # Initalize our image dictionaries
            self.setup_epic_dscovr()
            if self.natural_image_dict is None:
                self.natural_image_dict = {}
            if self.enhanced_image_dict is None:
                self.enhanced_image_dict = {}

        self.NASA_API_TOKEN = os.environ.get('NASA_API_TOKEN')
        if self.NASA_API_TOKEN is None:
            print(
                "Missing env variable NASA_API_TOKEN. Please sign up at api.nasa.gov to continue")
            return None

    def setup_epic_dscovr(self):
        # self.root_url = 'https://api.nasa.gov/EPIC/api'
        self.root_url = 'https://epic.gsfc.nasa.gov/api'
        # self.archive_url = 'https://api.nasa.gov/EPIC/archive'
        self.archive_url = 'https://epic.gsfc.nasa.gov/archive'
        if self.product_type is apiType.EPICDSCOVR:
            self.natural_image_dict = self.__fetch_data_from_file(
                'natural_images.pk')
            self.enhanced_image_dict = self.__fetch_data_from_file(
                'enhanced_images.pk')

    def index(self):
        if self.product_type is apiType.EPICDSCOVR:
            print(f"Indexing target {self.product_type.value}")
            self.index_epic_dscovr()

    def index_epic_dscovr(self):
        # available_dates_dict_url = 
        # 'https://epic.gsfc.nasa.gov/api/natural/all' # This is an undocumented endpoint
        available_dates_dict_url = f'{self.root_url}/natural/all?api_key={self.NASA_API_TOKEN}'

        # Build our URL with API key, query the endpoint, and 
        # convert the return data in to a usable list
        available_dates_dict = self.fetch_json_from_url(
            available_dates_dict_url)

        

        # Loop through the available dates
        for date in available_dates_dict:

            # Create our URL for fetching all the images available on a specific date
            if 'error' in date:
                print('You are being rate limited, slow down partner!')
                break
            date_text = date['date']
            natural_url = f'{self.root_url}/natural/date/{date_text}?api_key={self.NASA_API_TOKEN}'
            enhanced_url = f'{self.root_url}/enhanced/date/{date_text}?api_key={self.NASA_API_TOKEN}'

            # Only attempt to index previously indexed dates
            if date_text not in self.natural_image_dict:
                print(f'fetching natural date: {date_text}')
                self.natural_image_dict[date_text] = []
                temp_natural_image_list = self.fetch_json_from_url(natural_url)
                for item in temp_natural_image_list:
                    self.natural_image_dict[date_text].append(item)

                # Store our indexed data om a local file
                self.__store_data_in_file(
                    'natural_images.pk', self.natural_image_dict)
            else:
                print(f'Already indexed natural {date}')

            if date_text not in self.enhanced_image_dict:
                print(f'fetching enhanced date: {date_text}')
                self.enhanced_image_dict[date_text] = []

                temp_enhanced_image_list = self.fetch_json_from_url(
                    enhanced_url)

                for item in temp_enhanced_image_list:
                    self.enhanced_image_dict[date_text].append(item)

                self.__store_data_in_file(
                    'enhanced_images.pk', self.enhanced_image_dict)
            else:
                print(f'Already indexed enhanced {date}')

        print(
            f'found {len(self.natural_image_dict)} natural images and {len(self.enhanced_image_dict)}')

    def download_epic_dscovr_files(self, type='natural'):
        # We have two types of images provided by the EPIC DSCOVR satellite.
        # It's important to keep them separated.
        if type == 'natural':
            for date in self.natural_image_dict:
                for item in self.natural_image_dict[date]:
                    self.download_epic_dscovr_item(item, 'natural', date)
        if type == 'enhanced':
            for date in self.enhanced_image_dict:
                for item in self.enhanced_image_dict[date]:
                    self.download_epic_dscovr_item(item, 'enhanced', date)

        print('Finished downloading all indexed EPIC DSCOVR images')

    def download_epic_dscovr_item(self, item, type, date):
        # Make sure we have a valid item before even trying anything
        if len(item) < 1:
            return None

        # Set auxilary variables
        temp_filename = item['image']
        filename = f'{temp_filename}.png'

        # Construct our URL, see https://api.nasa.gov/ for documentation
        date_key = date.replace('-', '/')
        url = f'{self.archive_url}/{type}/{date_key}/png/{filename}?api_key={self.NASA_API_TOKEN}'

        # Create our folder structure for the downloaded images
        date_folder = date.replace('-', '')
        output_folder = f'./epic_dscovr/{type}/{date_folder}'
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)

        # Create our now completed local path for downloading our image
        output_filepath = f'{output_folder}/{filename}'

        # Validate if the image has been downloaded or not yet
        if not os.path.isfile(output_filepath):
            print(f'Downloading {filename} to {output_folder}...')
            self.download_image(url, output_filepath)
        else:
            print(f'Previously downloaded {filename} to {output_folder}')

    def fetch_json_from_url(self, url):
        # Implement GET request and load the JSON to an object
        output = requests.get(url)
        return json.loads(output.text)

    def __store_data_in_file(self, filename, data):
        # Dump the data in to pickle a file
        with open(filename, 'wb') as file:
            pickle.dump(data, file)

    def __fetch_data_from_file(self, filename):
        # Retrieve our pickle file to an object
        output = None
        try:
            with open(filename, 'rb') as file:
                output = pickle.load(file)
        except:
            print(f'Unable to open {filename}')
            return None
        return output

    def download_image(self, target_url, output_filepath):
        # Fetch our target_url
        response = requests.get(target_url, stream=True)

        # Write our image to a file
        with open(output_filepath, "wb") as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)

    def make_epic_dscovr_video(self, image_type='natural'):
        # This function will sort our images in to a bucket with proper naming
        picture_root_folder = f'./epic_dscovr/{image_type}'
        list_of_pictures = []
        if image_type == 'natural':
            for item in self.natural_image_dict:
                for picture in self.natural_image_dict[item]:

                    date_folder = item.replace('-', '')
                    time = picture['identifier']
                    filename = picture['image']
                    local_filepath = f'{picture_root_folder}/{date_folder}/{filename}.png'

                    if not os.path.isfile(local_filepath):
                        print(f'Missing local copy of {local_filepath}')
                        date_key = item.replace('-', '/')
                        url = f'{self.archive_url}/{image_type}/{date_key}/png/{filename}?api_key={self.NASA_API_TOKEN}'
                        self.download_image(url, local_filepath)

                    list_of_pictures.append((time, local_filepath))
        list_of_pictures.sort()

        photo_output_folder = 'output'
        if not os.path.isdir(photo_output_folder):
            os.mkdir(photo_output_folder)

        for index, photo in enumerate(list_of_pictures):
            source_path = photo[1]
            filename = str(index).zfill(4)
            destination_path = f'{photo_output_folder}/img{filename}.png'
            shutil.copy(source_path, destination_path)

        # command_to_make_video = 'ffmpeg -i img%07d.png -framerate 24 output.mp4'
        command_to_make_video = ['ffmpeg', '-framerate', '15', '-i',
                                 f'{photo_output_folder}/img%04d.png',  f'{photo_output_folder}/output.mp4']

        # NOTE: Notice how we are calling the subproces here using a LIST and NOT a string!
        # This means we don't need to use shell=True, which is VERY dangerous
        subprocess.Popen(command_to_make_video).wait()

        print('Finished making the requested video')
