import requests
from bs4 import BeautifulSoup as bs
import os, sys

'''
Final version that can download both through index or trough pages
'''

# For a manual approach you can change the parameters here
folder = ""
url = ""

def parser(url):
    '''Parse with beautiful soup the url'''
    return bs(requests.get(url).content,'html.parser')
def find_image(html):
    '''If it's an page, returns the title and the link to download'''
    image = ""
    for links in html.find_all('img'):
        if links.get('itemprop') == 'image': image = links
    if image:
        # Conseguir titulo
        for link in html.find_all('h2'):
            if link.get('itemprop') == 'name': title = link.string
        # Conseguir link
        for link in html.find_all('img'):
            if link.get('itemprop') =='image': source = link.get('src')
        return (title,source)
    else: return False
def download_image(title,source):
    flag = True
    while flag:
        print(f"Trying to download: {title}", end='')
        nome = title + '.png'
        if not os.path.isfile(nome): 
            with open(nome,"wb") as file: 
                file.write(requests.get(source).content)
        else: print(" It's already downloaded", end='')
        
        #Checking to see if it downloaded
        if os.path.getsize(nome) > 67: # Smallest possible png
            print(' Concluded'); flag = False
        else: 
            print(" Something went wrong, trying again")
            os.remove(nome)

def paged(html,other_list = []):
    print("It's paged download")
    # saves a list of everything that already downloads and new stuff
    flag = True
    lista = other_list
    global url
    new_url = url
    new_html = html
    new_lista = []
    print(url)

    while flag:
        download_image(*find_image(new_html))
        lista.append(new_url)

        for link in new_html.find_all("a", class_="item-portalitem-art"):
            new_url = link.get('href')
            if (new_url not in lista) and (new_url not in new_lista): new_lista.append(new_url)

        if not new_lista: 
            flag = False
        else: 
            new_url = new_lista.pop(0)
            new_html = parser(new_url)
            print(new_url)

            
def index(html):
    print("It's indexed download")
    lista = []

    # First will get all links in the image
    for links in html.find_all('a', class_='item-portalitem-art'):
        link = links.get('href')
        if link not in lista: lista.append(link)
    print(lista)
    for links in lista:
        html = parser(links)
        print(links)
        teste = find_image(html)
        if teste: download_image(*teste)

        # It will enter in a paged download if it finds an item not in the index
        for teste in html.find_all("a", class_="item-portalitem-art"):
            new_url = teste.get('href')
            if new_url not in lista: 
                paged(parser(new_url),lista)
                print("Returning to index")

if __name__ == "__main__":
    # Check if it's passed a folder or url in the arguments
    for i in sys.argv:
        args = i.split('=')
        if len(args) == 2:
            if args[0] == 'url': url = args[1]
            elif args[0] == 'folder': folder = args[1]

    # Try to create a folder in the place
    place = os.path.join(os.path.dirname(os.path.realpath(__file__)), folder)
    try: os.mkdir(place)
    except FileExistsError: print("The folder already exists")
    os.chdir(place)

    html = parser(url)

    if teste := find_image(html): paged(html)
    else: index(html)
