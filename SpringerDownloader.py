from bs4 import BeautifulSoup
import requests
import os
import time
import pandas as pd
from clint.textui import progress
import json

data = pd.read_excel("Book_Links.xlsx")

links = data['OpenURL'].to_numpy()
names = data['Book Title'].to_numpy()


base_link = 'https://link.springer.com/content/pdf/'
download_no = 0
fail_list = {}

for number, name in enumerate(names):
    print("Start Downloading " + name)
    current_link = links[number]
    print("Its Link: " + current_link)

    try:
        enter_response = requests.get(current_link)
        pdf_link = base_link + enter_response.url.split('/')[-1] + '.pdf'
        print("PDF Link: " + pdf_link)

        start = time.time()

        print("Downloading Begins...")
        pdf_response = requests.get(pdf_link, stream=True)
        print("Get it!")

        print("Calculating Size...")
        total_length = int(pdf_response.headers.get('content-length'))
        print('Total Length: ' + str(total_length))

        with open('./Books/' + name + '.pdf', 'wb') as pdf_file:
            for chunk in progress.bar(pdf_response.iter_content(chunk_size=100000),
                                      expected_size=(total_length / 100000) + 1):
                if chunk:
                    pdf_file.write(chunk)
                    pdf_file.flush()
        print(name + ' Downloaded')

        download_no += 1
        print("Total: " + str(download_no))

        print("Used Time: " + str(time.time() - start))
        print("Finished Downloading.")

        time.sleep(0.1)
    except:
        print('Error!')
        fail_list[name] = current_link
        with open('Fail.json', 'w') as fp:
            json.dump(fail_list, fp)

