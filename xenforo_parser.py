import requests
import argparse
import codecs
import time
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from html2bbcode.parser import HTML2BBCode
from bs4 import BeautifulSoup



API_SETTINGS = []

def get_html(url, sleep_time=0):
    chrome_options = Options()
    chrome_options.add_argument("headless")
    browser = webdriver.Chrome(options=chrome_options) 
    browser.get(url)             
    # if there is protection with a delay before entering the page
    time.sleep(sleep_time)              
    
    html = browser.page_source   
    browser.quit()               
    return html

def autoposting_settings():
    api_url = input('Enter a link to your API (<XF url>/api/): ')
    api_key = input('Enter your user API key: ')
    node_id = input('Enter your node id: ')

    r = requests.post(api_url, headers={'XF-Api-Key': api_key})

    if r.json()['errors'][0]['code'] == 'api_key_not_found':
        print("Invalid API key")
    else:
        global API_SETTINGS
        API_SETTINGS = [api_url, api_key, int(node_id)]

def api_create_thread(title, message, tags):
    print(API_SETTINGS)
    header = {'XF-Api-Key': API_SETTINGS[1]}
    param = {"node_id": API_SETTINGS[2], "title": title, "message": message.replace("\"", "'"), "tags": tags}
    requests.post(API_SETTINGS[0] + "threads/", params=param, headers=header)

def parse_content(forum_url, sleep_time, autoposting):
    bbcode_parser = HTML2BBCode()
    base_html = get_html(forum_url, sleep_time)
    base_url = re.search('.+\.[a-zA-Z]+/', forum_url)[0]
    base_folder = re.search('://(.+)/', base_url)[0][3:-1]

    if autoposting == False:
        try:
            os.mkdir(base_folder)
            print(f'Folder with name {base_folder} successfully created')
        except FileExistsError:
            print(f'Folder with name "{base_folder}" already exists')

    bs = BeautifulSoup(base_html, 'html5lib')
    forum_structItemContainer = bs.find(class_ = 'structItemContainer')
    threads = forum_structItemContainer.find_all('a', {'data-xf-init': 'preview-tooltip'})
    threads_links = []
    
    for thread in threads:       
        threads_links.append(base_url + thread.get('href'))
    for thread_link in threads_links:
        thread_tags = []
        thread_html = get_html(thread_link)
        thread = BeautifulSoup(thread_html, 'html5lib')
        thread_title = thread.find('h1', {'class': 'p-title-value'}).text
        # print(thread_title)
        thread_tagList = thread.find('span', {'class': 'js-tagList'})
        if thread_tagList is not None:
            for tag_text in thread_tagList.find_all('a'):
                thread_tags.append(tag_text.text)
        # print(thread_tags)
        thread_creator = thread.find('h4', {'class': 'message-name'}).text
        # print(thread_creator)
        thread_content = thread.find('div', {'class': 'bbWrapper'})
        thread_content = str(bbcode_parser.feed(str(thread_content)[23:-6]))
        print(thread_content)
        if API_SETTINGS is not None and autoposting == True:
            api_create_thread(thread_title, thread_content, thread_tags)
        else:
            try:
                thread_file = thread_link.replace(base_url,"").replace("/","").replace("threads", "")
                file = codecs.open(base_folder + '/' + thread_file + '.txt', 'w+', 'utf-8')
                content = f'Thread title:\n{thread_title}\n\n' \
                        f'Thread tags:\n{thread_tags}\n\n' \
                        f'Thread creator:\n{thread_creator}\n\n' \
                        f'Thread text:\n{thread_title}'
                file.write(content)
                file.close()
                print(f'Threade {thread_file} successfully saved\n')
            except Exception as exc:
                print(f'An error occurred while saving the theme: {exc}')

def main():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--url', '-u',
                        help='link to the forum page')
    # parser.add_argument('--login', '-l', 
    #                     help='username to log in to your account if necessary')
    # parser.add_argument('--password', '-p', 
    #                     help='password to log in to your account if necessary')
    parser.add_argument('--sleep', '-s', 
                        help='waiting time before logging in to the forum', type=int, default=0)
    parser.add_argument('--autoposting', '-a', 
                        help='automatically create topics on your forum using the REST API', action='store_true', default=False)
    args = parser.parse_args()
    if args.autoposting:
        autoposting_settings()

    parse_content(args.url, args.sleep, args.autoposting)

if __name__ == '__main__':
    main()