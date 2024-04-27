# Import necessary libraries
import ftplib
import requests
from PIL import Image
import io
from bs4 import BeautifulSoup
from datetime import datetime

# Get Met Office Data and Strip Today/Tonight Text
url = 'http://datapoint.metoffice.gov.uk/public/data/txt/wxfcs/regionalforecast/xml/512?key=YOURMETOFFICEAPIKEY'
document = requests.get(url)
soup = BeautifulSoup(document.content, "lxml-xml")

# Extract today's weather forecast
todayraw = soup.find_all("Paragraph", attrs={'title': 'Today:'})
todaystr = str(todayraw)
today = (todaystr.replace('[<Paragraph title="Today:">', '').replace('</Paragraph>', '').replace(']', ''))

# Set up OpenAI API key
from openai import OpenAI
client = OpenAI(api_key='YourOpenAIAPIKey')

# FTP server details
ftp_server = 'YourFTPServer'
ftp_username = 'FTPUserName'
ftp_password = 'FTPPassword'

# Specify the type of Norfolk landscape (e.g., rural, coastal, urban)
landscape_type = "rural Norfolk landscape"  # Change this as per your preference

# Create the image prompt
image_prompt = (
    f"A photorealistic single, cohesive scene image of a {landscape_type}, showcasing the following weather conditions: {today}. "
    "The image should realistically depict elements like cloud formations, sunlight or lack thereof, any precipitation, and wind effects. "
    "It should convey the atmosphere and mood suggested by the weather, with appropriate lighting and color tones. No numerical data or text should be included, just a pure visual representation of the weather in the landscape."
)

# Generate an image using OpenAI's DALL·E
def generate_image(prompt):
    response = client.images.generate(prompt=prompt, n=1, model="dall-e-3", quality="standard", style="vivid", size="1792x1024")
    image_url = response.data[0].url
    return image_url

# Function to generate a datestamp
def get_datestamp():
    return datetime.now().strftime("%Y%m%d%H%M%S")

# Modified FTP upload function
def upload_to_ftp(image_url, remote_path):
    with ftplib.FTP(ftp_server) as ftp:
        ftp.login(user=ftp_username, passwd=ftp_password)
        response = requests.get(image_url)
        image = Image.open(io.BytesIO(response.content))
        datestamp = get_datestamp()
        original_image = io.BytesIO()
        image.save(original_image, format='JPEG')
        original_image.seek(0)
        ftp.storbinary(f'STOR {remote_path}_{datestamp}.jpeg', original_image)
        resized_image = image.resize((1792, 1024))
        jpeg_image = io.BytesIO()
        resized_image.save(jpeg_image, format='JPEG')
        jpeg_image.seek(0)
        ftp.storbinary('STOR public_html/image.jpeg', jpeg_image)
        resized_image = image.resize((800, 480))
        jpeg_image = io.BytesIO()
        resized_image.save(jpeg_image, format='JPEG')
        jpeg_image.seek(0)
        ftp.storbinary('STOR public_html/image_eink.jpeg', jpeg_image)

# Generate the image and upload it
image_url = generate_image(image_prompt)
upload_to_ftp(image_url, 'public_html/image.jpeg')
