import os
from datetime import datetime, timedelta
import pickle
import requests
import subprocess
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request

# Later support of Apple Photos, Dropboox, Live.com/Onedrive, etc
platform = 'google'



SCOPES = ['https://www.googleapis.com/auth/photoslibrary.readonly']

creds = None
if os.path.exists('token.pickle'):
    with open('token.pickle', 'rb') as token:
        creds = pickle.load(token)

if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file('creds.json', SCOPES)
        creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

DISCOVERY_URL = ('https://photoslibrary.googleapis.com/$discovery/rest?version=v1')
service = build('photoslibrary', 'v1', credentials=creds, discoveryServiceUrl=DISCOVERY_URL)


results = service.mediaItems().list(pageSize=10).execute()
items = results.get('mediaItems', [])

def get_media_items_same_day(service, years_back=5, page_size=100, start=None):
    if (start != None):
        today=datetime.strptime(start,'%Y-%m-%d')
    else:
        today = datetime.now()
    month_day = (today.month, today.day)
    
    date_ranges = []

    for i in range(1, years_back+1):
        past_year = today.year - i
        start_date = datetime(past_year, month_day[0], month_day[1])
        end_date = start_date + timedelta(days=1)
        date_range = {
            'startDate': {
                'year': start_date.year,
                'month': start_date.month,
                'day': start_date.day
            },
            'endDate': {
                'year': end_date.year,
                'month': end_date.month,
                'day': end_date.day
            }
        }
        date_ranges.append(date_range)

    request_body = {
        'filters': {
            'dateFilter': {
                'ranges': date_ranges
            }
        },
        'pageSize': page_size
    }

    request = service.mediaItems().search(body=request_body)
    response = request.execute()
    print(date_ranges)
    return response.get('mediaItems', [])

# Get media items
media_items = get_media_items_same_day(service)
year = datetime.now().year - 5
day = datetime.now().day
month = datetime.now().month


def download_media_items(media_items, local_path):
    if not os.path.exists(local_path):
        os.makedirs(local_path)

    for item in media_items:
        file_name = item['filename']
        image_url = item['baseUrl'] + '=d'  # '=d' retrieves the image in its original resolution
        response = requests.get(image_url)

        if response.status_code == 200:
            with open(os.path.join(local_path, file_name), 'wb') as f:
                f.write(response.content)
        else:
            print(f"Failed to download {file_name} from URL: {image_url}")

# Specify your local directory path
local_directory_path = '/home/pi/images/'

# Download media items to the specified local directory
download_media_items(media_items, local_directory_path)



def convert_heic_to_jpeg(input_dir):
    for root, _, files in os.walk(input_dir):
        print ("{} total files to process.".format(len(files)))
        for file in files:
            if file.lower().endswith('.heic'):
                input_file_path = os.path.join(root, file)
                output_file_path = os.path.join(root, file[:-4] + 'jpg')
                
                # Convert the HEIC image to JPEG
                #subprocess.run(["magick", input_file_path, output_file_path])
                subprocess.run(["convert", input_file_path, output_file_path])
                
                # Copy the metadata
                subprocess.run(["exiftool", "-tagsFromFile", input_file_path, "-all:all", output_file_path])
                print("editing file {}".format(output_file_path))                
                # Remove temporary files created by exiftool
                if os.path.exists(output_file_path + "_original"):
                    os.remove(output_file_path + "_original")

# Call the function with the directory containing your HEIC files
convert_heic_to_jpeg("/home/pi/images/")


#print("executing the rm command remotely...")
#subprocess.run(["ssh", "-p", "22222", "root@homeassistant.local", "'rm -f /media/*.jpg'"])
#print("executing the copy command to the remote directory...")
#subprocess.run(["scp", "-P","22222", "/home/pi/images/*.jpg",  "root@homeassistant.local:/media/."])
