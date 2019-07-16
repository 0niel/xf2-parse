import time
from bs4 import BeautifulSoup
import requests
import codecs
import re
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def get_html(url): #передаем URL
    chrome_options = Options()
    chrome_options.add_argument("headless")
    
    browser = webdriver.Chrome(chrome_options=chrome_options) 
    browser.get(url)             

    time.sleep(0)               #если есть защита с задержкой на вход 
    
    html = browser.page_source   

    browser.quit()               
    return html                  
def main():
    pages = ['https://blast.hk/forums/53']
    print('pages:', '; '.join(pages))
    for base_page in pages:
        print('base_page:', base_page)
        base = re.search('.+\.[a-zA-Z]+/', base_page)[0]
        base_folder = re.search('://(.+)/', base)[0][3:][::-1][1:][::-1]
        base_html = get_html(base_page)

        print()

        try:
            os.mkdir(base_folder)
            print(f'Folder with name {base_folder} successfully created')
        except FileExistsError:
            print(f'Folder with name "{base_folder}" already exists')
        print()

        bs = BeautifulSoup(base_html, 'html5lib')

        themes_ol = bs.find(class_ = 'structItemContainer')
        themes_bs = BeautifulSoup(str(themes_ol), 'html5lib')
        themes = themes_bs.find_all('a', {'data-xf-init': 'preview-tooltip'})

        themes_links = [(base + theme.attrs['href']) for theme in themes]
        ind = 1
        for theme_link in themes_links:
            print(f'[{ind}/{len(themes_links)}] theme_link:', theme_link)

            theme_html = get_html(theme_link)
            theme_bs = BeautifulSoup(theme_html, 'html5lib')

            theme_name = theme_bs.find('h1', {'class': 'p-title-value'}).text
            print(theme_name)
            theme_tags = '; '.join([tag.text for tag in BeautifulSoup(str(theme_bs.find('span', {'class': 'js-tagList'})), 'html5lib').find_all('a', {'class': 'tagItem'})])
            theme_creator = theme_bs.find('h4', {'class': 'message-name'}).text.split()[0]
            print(theme_tags, theme_creator)
            theme_text = theme_bs.find('div', {'class': 'bbWrapper'})
            
            theme_attachments_tmp = BeautifulSoup(str(theme_bs.find('ul', {'class': 'attachmentList'})), 'html5lib').find_all('li', {'class': 'attachment'})
            theme_attachments_lst = []
            for theme_attachment in theme_attachments_tmp:
                attachment_link = base + '/' + BeautifulSoup(str(theme_attachment), 'html5lib').find('div', {'class': 'attachment-name'}).find('a').attrs['href']
                attachment_text = BeautifulSoup(str(theme_attachment), 'html5lib').find('a').text
                theme_attachments_lst.append(f'{attachment_text}: {attachment_link}')
            theme_attachments = '\n'.join(theme_attachments_lst)

            theme_file = theme_link[::-1][1:][::-1]
            while '/' in theme_file:
                theme_file = theme_file[1:]
            try:
                file = codecs.open(base_folder + '\\' + theme_file + '.txt', 'w+', 'utf-8')
                content = f'theme name:\n{theme_name}\n\n' \
                        f'theme tags:\n{theme_tags}\n\n' \
                        f'theme creator:\n{theme_creator}\n\n' \
                        f'theme attachments:\n{theme_attachments}' \
                        f'theme text:\n{theme_text}'
                file.write(content)
                file.close()
                print(f'theme with number {theme_file} successfully saved\n')
            except Exception as exc:
                print(f'an error occurred while saving the theme: {exc}')
            ind += 1
        
 
if __name__ == '__main__':
    main()