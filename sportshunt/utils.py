from urllib.parse import urlencode

def construct_next_url(base_url, next_path):
    query_string = urlencode({'next': next_path})
    return f'{base_url}?{query_string}'