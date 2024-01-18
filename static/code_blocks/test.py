
import requests

def get_random_quote():
    url = 'https://api.quotable.io/random'
    response = requests.get(url)
    quote = response.json()['content']
    author = response.json()['author']
    return f'"{quote}" - {author}'

quote = get_random_quote()
print("Here's a random quote for you:")
print(quote)
