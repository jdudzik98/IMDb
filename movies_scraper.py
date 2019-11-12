from bs4 import BeautifulSoup
import requests

movies_links = []
page = requests.get('https://www.imdb.com/search/title/?title_type==feature&release_date=2018-01-01,2018-12-31&sort=' +
                    'boxoffice_gross_us,asc&count=250&start=' + str(0+1) + '&ref_=adv_nxt')

soup = BeautifulSoup(page.text, 'html.parser')
movies = soup.find_all(class_='lister-item mode-advanced')

for movie in movies:
    single_movie = movie.find(class_='lister-item-image float-left').find('a')['href']
    movies_links.append(single_movie)

print(movies_links)
