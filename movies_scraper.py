from bs4 import BeautifulSoup
import requests
import time

movies_links = []
for single_page in range(int(11897/250)):
    broken = False
    page = requests.get(
        'https://www.imdb.com/search/title/?title_type=feature&release_date=2018-01-01,2018-12-31&sort=' +
        'boxoffice_gross_us,asc&count=250&start=' + str(single_page*250 + 1) + '&ref_=adv_nxt')

    soup = BeautifulSoup(page.text, 'html.parser')
    movies = soup.find_all(class_='lister-item mode-advanced')

    for movie in movies:
        movie_href = movie.find(class_='lister-item-image float-left').find('a')['href']
        single_movie = movie.find(class_="sort-num_votes-visible").find_all('span', {"name": "nv"})

        # conditional statement to exclude movies without known box office
        if str(single_movie[0].contents[0][0]) == '$':
            movies_links.append(movie_href)
        else:
            try:
                if str(single_movie[1].contents[0][0]) == '$':
                    movies_links.append(movie_href)
                else:
                    broken = True
                    print("Unknown Error")
            except IndexError:
                broken = True
                break
    if broken:
        break
    time.sleep(1)


def fetch_box_office(href):
    page2 = requests.get('https://www.imdb.com' + str(href))
    soup2 = BeautifulSoup(page2.text, 'html.parser')
    movie_details = soup2.find(id="titleDetails")
    try:
        txt = movie_details.find_all(class_="txt-block")
        for t in txt:
            try:
                header = t.find(class_="inline").contents
                if 'Cumulative Worldwide Gross' in str(header[0]):
                    return str(t.contents[2])
            except AttributeError:
                return "NA"
    except ValueError:
        pass