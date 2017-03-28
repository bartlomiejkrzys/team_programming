import os
import json
from wsgiref import simple_server
from collections import namedtuple
from itertools import starmap

from jinja2 import Environment, FileSystemLoader

import falcon

import settings


# Server conf
PORT = settings.SERVER_PORT
HOST = settings.SERVER_HOST
# Site conf
TEMPLATE_NAME = settings.INDEX_HTML_NAME
# Data conf
SEPERATOR = settings.DATA_SEPERATOR
THIS_DIR = os.path.dirname(os.path.abspath(__file__))

J2_ENV = Environment(loader=FileSystemLoader(THIS_DIR),
                     trim_blocks=True)
Probe = namedtuple('Probe', 'humidity temperature height')


def get_chunks(data, size):
    '''
    Args:
        data: SEQUENCE: Sequence of data to be chunked
        size: INT: size of each chunk of data
    Output:
        Generator producing chunks of data.
    Chunk data to pieces of given size. 
    When data length is not divisible by size,
    the last chunk will be at size of len(data) % size.
    '''
    for idx in range(0, len(data), size):
        yield data[idx: idx + size]

def is_not_damaged(probe):
    '''
    Args:
        probe: SEQUENCE: Sequence of data
    Output:
        BOOL: True if 0 not found in probe else False
    Check if probe is not damaged by checking
    if any value inside is equal to 0
    
    '''
    return 0 not in probe


def payload(bstring):
    '''
    Args:
        bstring: BYTE STRING: data to be processed
    Output:
        LIST: list of filtered tuples containing data about 
              humidity, temperature and height.
    '''
    data = list(map(int, bstring.split(SEPERATOR)))
    chunked_data = get_chunks(data, 3)
    filtered_data = list(filter(is_not_damaged, chunked_data))
    labeled_data = list(starmap(Probe, filtered_data))
    return labeled_data


class Site(object):
    def __init__(self, data):
        self.data = data
    def on_get(self, request, response):
        index_html_content = J2_ENV.get_template(TEMPLATE_NAME).render(Greeting="EY! WHATCHA LOOKIN FOR!")
        response.content_type = 'text/html'
        response.body = index_html_content


class JSONSerializer(object):
    def __init__(self, data):
        self.data = data
    
    def on_get(self, request, response, id):
        if -2 < int(id) < len(self.data):
            data = self.get_json_data(int(id))  
            response.content_type = 'application/json'
            response.status = falcon.HTTP_200
            response.body = data
        else:
            response.status = falcon.HTTP_404
            response.body = self.id_out_of_range_msg()

    def get_json_data(self, id):
        if id == -1:
            data = list(map(Probe._asdict, self.data))
            return json.dumps(data)
        else:
            data = dict(self.data[id]._asdict())
            return json.dumps(data)
    
    def id_out_of_range_msg(self):
        return "json/(id) must be in range of -1 <= id <= {}".format(len(self.data) - 1)


def get_data():
    return payload(b'1,2,3,4,5,6,7,8,0,11,4,3')

data = get_data()

app = falcon.API()
app.add_route('/', Site(data))
app.add_route('/json/{id}', JSONSerializer(data))
server = simple_server.make_server(HOST, PORT, app)
if __name__ == '__main__':
    print('Server running at HOST={HOST} PORT={PORT}'.format(**locals()))
    server.serve_forever()
