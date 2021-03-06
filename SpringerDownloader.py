# from bs4 import BeautifulSoup
# import requests
# import os
# import time
# import pandas as pd
# from clint.textui import progress
# import json
#
# data = pd.read_excel("Book_Links.xlsx")
#
# links = data['OpenURL'].to_numpy()
# names = data['Book Title'].to_numpy()
#
#
# base_link = 'https://link.springer.com/content/pdf/'
# download_no = 0
# fail_list = {}
#
# for number, name in enumerate(names):
#     print("Start Downloading " + name)
#     current_link = links[number]
#     print("Its Link: " + current_link)
#
#     try:
#         enter_response = requests.get(current_link)
#         pdf_link = base_link + enter_response.url.split('/')[-1] + '.pdf'
#         print("PDF Link: " + pdf_link)
#
#         start = time.time()
#
#         print("Downloading Begins...")
#         pdf_response = requests.get(pdf_link, stream=True)
#         print("Get it!")
#
#         print("Calculating Size...")
#         total_length = int(pdf_response.headers.get('content-length'))
#         print('Total Length: ' + str(total_length))
#
#         with open('./Books/' + name + '.pdf', 'wb') as pdf_file:
#             for chunk in progress.bar(pdf_response.iter_content(chunk_size=100000),
#                                       expected_size=(total_length / 100000) + 1):
#                 if chunk:
#                     pdf_file.write(chunk)
#                     pdf_file.flush()
#         print(name + ' Downloaded')
#
#         download_no += 1
#         print("Total: " + str(download_no))
#
#         print("Used Time: " + str(time.time() - start))
#         print("Finished Downloading.")
#
#         time.sleep(0.1)
#     except:
#         print('Error!')
#         fail_list[name] = current_link
#         with open('Fail.json', 'w') as fp:
#             json.dump(fail_list, fp)



from bs4 import BeautifulSoup
import requests
import os
import time
from clint.textui import progress

URL = 'https://docs.google.com/spreadsheets/d/1HzdumNltTj2SHmCv3SRdoub8SvpIEn75fa4Q23x0keU/htmlview#gid=793911758'

pdf_base_URL = 'https://link.springer.com'

response = requests.get(URL)
response.raise_for_status()

soup = BeautifulSoup(response.content, 'lxml')

book_shelf = soup.find_all('tr')


def get_user_choice(books):
    print('\n\n---Welcome to Free Springer E-Books Store---')
    print('--------------------------------------------')
    print('******** Available E-Book Packages ********')
    print('--------------------------------------------')

    for package_name in books:
        print('| {} '.format(package_name), end='\n')

    while True:
        print('\nPress 1: View the list of available E-books by package names')
        print('Press 2: Download specific e-books')
        print('Press 3: Download all e-books from SPECIFIC packages')
        print('Press 4: Download all e-books from ALL packages')
        print('Press 0: Quit')

        choice = int(input('\nEnter your choice: '))

        if choice not in (1, 2, 3, 4, 0):
            print('\nWrong choice!! Enter again!!\n')
        else:
            break

    return choice


def collect_books_data():
    global book_shelf

    books = dict()

    for row in book_shelf[3:]:

        columns = row.find_all('td')
        book_title = columns[0].text
        author = columns[1].text
        package_name = columns[2].text
        book_download_link = columns[3].text

        if package_name not in books:
            books[package_name] = dict()

        if book_title not in books[package_name]:
            books[package_name][book_title] = {
                'Author': author,
                'Book Download Link': book_download_link
            }

    return books


def get_file_name(books, package_name, book_title):
    file_name = book_title + '_by_' + books[package_name][book_title]['Author'] + '.pdf'

    if len(file_name.split('/')) > 1:
        file_name = ' or '.join(file_name.split('/'))

    return file_name


def download_books(books):
    global pdf_base_URL

    print('\n\n-------- *** DOWNLOADING STARTED *** --------\n\n')

    for package_name in books:

        directory_path = os.path.join(os.getcwd(), package_name)

        if not os.path.exists(directory_path):
            os.mkdir(directory_path)

        print(f'---Downloading E-books from {package_name}---')

        for book_title in books[package_name]:

            file_name = get_file_name(books, package_name, book_title)

            file_path = os.path.join(directory_path, file_name)

            print(f'\nSearching "{book_title}" in the current directory -> ', end='')

            try:

                download_site_response = requests.get(books[package_name][book_title]['Book Download Link'])
                download_site_response.raise_for_status()

                soup2 = BeautifulSoup(download_site_response.content, 'lxml')

                links = soup2.select('a[data-track-action="Book download - pdf"]')

                pdf_query_URL = links[0]['href']

                pdf_response = requests.get(pdf_base_URL + pdf_query_URL, stream=True)
                pdf_response.raise_for_status()

                total_length = int(pdf_response.headers.get('content-length'))

                if not os.path.exists(file_path):

                    print("NOT FOUND")
                    time.sleep(1)

                    print(f'\nDownloading "{book_title}"...\n')

                    with open(file_path, 'wb') as pdf_file:

                        for chunk in progress.bar(pdf_response.iter_content(chunk_size=100000),
                                                  expected_size=(total_length / 100000) + 1):
                            if chunk:
                                pdf_file.write(chunk)
                                pdf_file.flush()

                    print(f'\n"{book_title}" DOWNLOAD STATUS: OK!!\n')

                else:

                    file_size = os.stat(f'{file_path}')[6]

                    if file_size != total_length:

                        print('INCOMPLETE/CURRUPTED FILE!')

                        print(f'\n"Re-downloding {book_title}"...\n')

                        with open(file_path, 'wb') as pdf_file:

                            for chunk in progress.bar(pdf_response.iter_content(chunk_size=100000),
                                                      expected_size=(total_length / 100000) + 1):
                                if chunk:
                                    pdf_file.write(chunk)
                                    pdf_file.flush()

                        print(f'\n"{book_title}" DOWNLOAD STATUS: OK!!\n')

                    else:

                        print('FOUND\n')
                        time.sleep(1)

            except:

                print('Some ERROR occurred')
                print('\nPOSSIBLE CAUSES: ')
                print('------------------------')
                print('* The book is not free any more')
                print('* The download link is changed or broken')
                print('* Source server is down')

    print('\n\n-----*** DOWNLOADING COMPLETED ***--------\n')


def get_packages_data():
    print("\n* Enter package names carefully!! Names are CASE SENSITIVE!!")
    print("* PUT Comma(,) between in case of multiple package names !!")
    packages = input('\nEnter package name(s): ')

    packages = packages.split(',')

    for i in range(len(packages)):
        packages[i] = packages[i].strip()

    return packages


def display_package_booklist(books, packages):
    for package in packages:

        index = 1

        print('\n\nShowing booklist for {}'.format(package))
        print('----------------------------------------------')

        for book_title in books[package]:
            print('| {}. {}   |by|   {}'.format(index, book_title, books[package][book_title]['Author']))
            index += 1


def get_specific_book_data(books):
    print('\nEnter details CAREFULLY !! Every details is CASE-SENSITIVE !!')

    while True:
        package_name = input('\nEnter the package name where the book belongs: ')
        if package_name not in books:
            print('\nWrong package name!! Check spelling/letter case/name properly before entering !!')
        else:
            break

    while True:
        book_title = input('\nEnter the book title: ')
        if book_title not in books[package_name]:
            print('\nWrong book title!! Check spelling/letter case/name properly before entering !!')
        else:
            break

    while True:
        author_name = input('\nEnter the name of the author(s) of the book: ')
        if author_name == books[package_name][book_title]:
            print('\nWrong author name!! Check spelling/letter case/name properly before entering !!')
        else:
            break

    return {
        package_name: {
            book_title: {
                'Author': author_name,
                'Book Download Link': books[package_name][book_title]['Book Download Link']
            }
        }
    }


def main():
    while True:

        books = collect_books_data()

        choice = get_user_choice(books)

        if choice == 0:
            print('\nThank you !! Please give a star to this repository on GitHub !!')
            exit()

        elif choice == 1:
            packages = get_packages_data()
            display_package_booklist(books, packages)

        elif choice == 2:
            single_book = get_specific_book_data(books)
            download_books(single_book)

        elif choice == 3:
            packages = get_packages_data()

            books2 = dict()

            for package_name in packages:
                books2[package_name] = books[package_name]

            download_books(books2)

        else:
            download_books(books)


main()