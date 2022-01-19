# Author: Amelia Wietting
# Date: 20220119

import requests
import os
import json
import pickle
import shutil

from enum import Enum

class apiType(Enum):
    EPICDSCOVR = "epicdscovr"

class projectEarth():
    def __init__(self,product_type=None):
        print("Welcome to Project Earth, starting up...")
        
        if product_type is None:
            print("Please select a valid api, the following are supported:")
            for type in apiType:
                print(type.name)
            return None
        
        self.product_type = product_type
        
        if self.product_type is apiType.EPICDSCOVR:
            self.setup_epic_dscovr()

        self.NASA_API_TOKEN = os.environ.get('NASA_API_TOKEN')
        if self.NASA_API_TOKEN is None:
            print("Missing env variable NASA_API_TOKEN. Please sign up at api.nasa.gov to continue")
            return None
    
    def setup_epic_dscovr(self):
        self.root_url = 'https://api.nasa.gov/EPIC/api'
        # self.root_url = 'https://epic.gsfc.nasa.gov/api'
        self.archive_url = 'https://api.nasa.gov/EPIC/archive'
        # self.archive_url = 'https://epic.gsfc.nasa.gov/archive'
        if self.product_type is apiType.EPICDSCOVR:
            self.natural_image_dict = self.__fetch_data_from_file('natural_images.pk')
            self.enhanced_image_dict = self.__fetch_data_from_file('enhanced_images.pk')
    
    def index(self):
        if self.product_type is apiType.EPICDSCOVR:
            self.setup_epic_dscovr()
            print(f"Indexing target {self.product_type.value}")
            self.index_epic_dscovr()
    
    def index_epic_dscovr(self):
        # available_dates_dict_url = 'https://epic.gsfc.nasa.gov/api/natural/all' # This is an undocumented endpoint
        available_dates_dict_url = f'{self.root_url}/natural/all?api_key={self.NASA_API_TOKEN}'
        
        # Build our URL with API key, query the endpoint, and convert the return data in to a usable list
        available_dates_dict = self.fetch_json_from_url(available_dates_dict_url)
        
        if self.natural_image_dict is None:
            self.natural_image_dict = {}
        if self.enhanced_image_dict is None:
            self.enhanced_image_dict = {}
        
        for date in available_dates_dict:

            date_text = date['date']
            natural_url = f'{self.root_url}/natural/date/{date_text}?api_key={self.NASA_API_TOKEN}'
            enhanced_url = f'{self.root_url}/enhanced/date/{date_text}?api_key={self.NASA_API_TOKEN}'
            if date_text not in self.natural_image_dict:
                print(f'fetching natural date: {date_text}')
                self.natural_image_dict[date_text] = [{}]
                temp_natural_image_list = self.fetch_json_from_url(natural_url)
                for item in temp_natural_image_list:
                    self.natural_image_dict[date_text].append(item)
                
                self.__store_data_in_file('natural_images.pk',self.natural_image_dict)
            else:
                print(f'Already indexed natural {date}')
            
            if date_text not in self.enhanced_image_dict:
                print(f'fetching enhanced date: {date_text}')
                self.enhanced_image_dict[date_text] = [{}]            
                
                temp_enhanced_image_list = self.fetch_json_from_url(enhanced_url)
                
                for item in temp_enhanced_image_list:
                    self.enhanced_image_dict[date_text].append(item)
                
                self.__store_data_in_file('enhanced_images.pk',self.enhanced_image_dict)
            else:
                print(f'Already indexed enhanced {date}')

        print(f'found {len(self.natural_image_dict)} natural images and {len(self.enhanced_image_dict)}')

    def download_epic_dscovr_files(self,type='natural'):
        if type == 'natural':
            for date in self.natural_image_dict:
                for item in self.natural_image_dict[date]:
                    self.download_epic_dscovr_item(item,'natural',date)
        if type == 'enhanced':
            for date in self.enhanced_image_dict:
                for item in self.enhanced_image_dict[date]:
                    self.download_epic_dscovr_item(item,'enhanced',date)

        print('Finished downloading all indexed EPIC DSCOVR images')    
        
    def download_epic_dscovr_item(self,item,type,date):
        if len(item) < 1:
            return None
        date_key = date.replace('-','/')
        date_folder = date.replace('-','')
        
        temp = item['image']
        filename = f'{temp}.png'

        url = f'{self.archive_url}/{type}/{date_key}/png/{filename}?api_key={self.NASA_API_TOKEN}'
        
        output_folder = f'./epic_dscovr/{type}/{date_folder}'
        if not os.path.isdir(output_folder):
            os.makedirs(output_folder)

        output_filepath = f'{output_folder}/{filename}'
        if not os.path.isfile(output_filepath):

            print(f'Downloading {filename} to {output_folder}...')
            self.download_image(url,output_filepath)
        else:
            print(f'Previously downloaded {filename} to {output_folder}')

    def fetch_json_from_url(self,url):
        output = requests.get(url)
        return json.loads(output.text)

    def __store_data_in_file(self,filename,data):
        # Dump the data in to a file
        with open(filename,'wb') as fi:
            pickle.dump(data,fi)
    
    def __fetch_data_from_file(self,filename):
        output = None
        try:
            with open(filename,'rb') as fi:
                output = pickle.load(fi)
        except:
            print(f'Unable to open {filename}')
            return None
        return output

    def download_image(self,target_url,output_filepath):
        
        response = requests.get(target_url, stream=True)

        with open(output_filepath, "wb") as file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, file)
        