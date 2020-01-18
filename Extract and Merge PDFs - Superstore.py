
# This example shows how to use the Tableau Server REST API
# to sign in to a server, get back an authentication token,  
# site ID, fetch PDFs, sign out, and merge the PDFs.
# I ran this example on Python 3.7

#pip install packages if not installed

import requests, json, getpass, os
import urllib.parse
from os import walk
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileMerger, PdfFileReader

# NOTE! Substitute your own values for the following variables

server_name = "https://10ax.online.tableau.com/"
user_name = "NYTableauDev@gmail.com"
password = "NDJNeSf5zLNt" #getpass.getpass() #use getpass() method in production
site_url_id = "nikuldev423951" #An empty string can used to specify the default site.
projectName = "Finance"

#Define name of the final Merged PDF
report_name = 'Merged PDF Report'
# Directory where to save individual PDFs and Merged PDF.
filepath_to_folders = "C:\\TableauPDF\\"
# folder to save individual PDF files
folder_name = "PDFs"
# folder to save final Merged PDF file
merge_folder_name = "Merged"
subfolder_names = [folder_name, merge_folder_name]
#set directory name for individual PDFs
pdfs_folder_directory = os.path.join(filepath_to_folders, folder_name)
#set directory name for Merged PDF
merge_folder_directory = os.path.join(filepath_to_folders, merge_folder_name)
#Create necessary folders if doesn't exist
for subfolder_name in subfolder_names:
    path = os.path.join(filepath_to_folders, subfolder_name)
    try:
        os.makedirs(path, exist_ok=True)
        print(f"Directory {subfolder_name} created successfully")
    except OSError as error:
        print(f"Directory {subfolder_name} can not be created")


#Use GetViewIDstoPDF.py to extract unique IDs of the views to create PDFs for. 

overview_view_id="dab38b32-0bf9-456f-9c56-23883b03d626" #name = "Overview:        "region
product_view_id="0f905500-2ce8-4b81-874c-e17ea7488a49" #name = "Product:         "region
ship_view_id="249ca211-359f-46fe-a115-4d753f25edea" #name = "Shipping:        "region
custmr_view_id="e6eccc7a-e551-443b-ae74-898dc51e7c54" #name = "Customers:       "category
order_view_id="ca42b25e-b35a-4138-be3b-f4c122f4eae6" #name = "Order Details:   "category

#Grouped above views in 2 buckets. One for "Region" related PDFs and the othe for "Category" related PDFs
region_views=[overview_view_id, product_view_id, ship_view_id]
category_views=[custmr_view_id, order_view_id]

#To showcase how to iterate 2 different filters on 2 sets of views
regions = ['Central', 'East', 'South', 'West']
#enoding filer list to make them ready to use in HTTP URL request. e.g. if the filter value was 'Office Supplies' then this will convert it to 'Office%20Supplies'
encoded_regions = []
for region_index, region_value in enumerate(regions):
    encoded_regions.append(urllib.parse.quote(region_value))

categories = ['Furniture', 'Office Supplies', 'Technology']
#enoding regions list to make them ready to use in HTTP URL request. e.g. if the filter value was 'Office Supplies' then this will convert it to 'Office%20Supplies'
encoded_categories = []
for category_index, category_value in enumerate(categories):
    encoded_categories.append(urllib.parse.quote(category_value))

#Authenticate a session. Following code block will sign in using API calls using variables defined at the top.
signin_url = f"{server_name}/api/3.1/auth/signin"		
payload = { "credentials": { "name": user_name, "password": password, "site": {"contentUrl": site_url_id }}}
headers = {
  'accept': 'application/json',
  'content-type': 'application/json'
}
					
# Send the request to the server
req = requests.post(signin_url, json=payload, headers=headers)
req.raise_for_status()
					
# Get the response
response = json.loads(req.content)

# Parse the response JSON. The response body will look similar
# to the following example:
#
# {
#	 "credentials": {
#		 "site": {
#			 "id": "xxxxxxxxxx-xxxx-xxxx-xxxxxxxxxx",
#			 "contentUrl": ""
#		 },
#		 "user": {
#			 "id": "xxxxxxxxxx-xxxx-xxxx-xxxxxxxxxx"
#		 },
#		  "token": "AUTH-TOKEN"
#	 }
# }
					
				
# Get the authentication token from the <credentials> element					
token = response["credentials"]["token"]
					
# Get the site ID from the <site> element
site_id = response["credentials"]["site"]["id"]
					
print('Sign in successful!')
print('\tToken: {token}'.format(token=token))
print('\tSite ID: {site_id}'.format(site_id=site_id))

					
# Set the authentication header using the token returned by the Sign In method.
headers['X-tableau-auth']=token

					
					
#calculate how many pages will be generated in total
pdf_count=len(region_views)*len(encoded_regions)+len(category_views)*len(encoded_categories)

print(f'Fetching your {pdf_count} PDFs...')

#For each region value, create URL request for each region for each region grouping view to create a PDF.
#If a page number is needed on the final merged PDF then create an INT Parameter named "[PDFPage]" on your workbook. Add that Parameter on all the views for PDF. URL already includes PDFPage argument.
 
count=1#0
for Region in encoded_regions:
    for region_view in region_views:
        pdf_url=f'{server_name}/api/3.1/sites/{site_id}/views/{region_view}/pdf?orientation=Landscape&vf_Region={Region}&vf_PDFPage={count}'
        pdf_request = requests.get(pdf_url, headers=headers,verify=True) 
        pdf_request.raise_for_status()
#        count = count + 1
        count_str = str(count).zfill(3)
        file_name=fr'{pdfs_folder_directory}\\PDF{count_str}.pdf'
        count = count + 1
        with open(file_name, 'wb') as f:
            f.write(pdf_request.content)
            print('\tSaved: '+file_name)

#For each category value, create URL request for each category for each category grouping view to create a PDF.
#If a page number is needed on the final merged PDF then create an INT Parameter named "[PDFPage]" on your workbook. Add that Parameter on all the views for PDF. URL already includes PDFPage argument.
for Category in encoded_categories:
    for category_view in category_views:
        pdf_url=f'{server_name}/api/3.1/sites/{site_id}/views/{category_view}/pdf?orientation=Landscape&vf_Category={Category}&vf_PDFPage={count}'
        pdf_request = requests.get(pdf_url, headers=headers,verify=True) 
        pdf_request.raise_for_status()
#        count = count + 1
        count_str = str(count).zfill(3)
        file_name=fr'{pdfs_folder_directory}\\PDF{count_str}.pdf'
        count = count + 1
        with open(file_name, 'wb') as f:
            f.write(pdf_request.content)
            print('\tSaved: '+file_name)

# # ... Make any other calls here ...

# Sign out
signout_url = f"{server_name}/api/3.1/auth/signout"
					
req = requests.post(signout_url, data=b'', headers=headers)
req.raise_for_status()
print('Sign out successful!')


print("Now Merging the PDFs")

#getting list of all individual PDFs to merge
os.chdir(pdfs_folder_directory) 
f = []
for (dirpath, dirnames, filenames) in walk(pdfs_folder_directory):
    f.extend(filenames)
    break
print(f)

#Merging all PDFs from the list above
merger = PdfFileMerger()
for filename in f:
    merger.append(PdfFileReader(filename, 'rb'))
    print("\tMerging "+ filename)

os.chdir(merge_folder_directory) 
report_name_full=fr'{report_name}.pdf'
merger.write(report_name_full)
print('Saved '+report_name_full+' in ' +merge_folder_directory)