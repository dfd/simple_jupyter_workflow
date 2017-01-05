from collections import namedtuple
from pathlib import Path

sources = namedtuple('SOURCES',['DOCKERFILE','DOCKERHUB','URL','GIT','LOCAL_IMAGE'])
SOURCES = sources('DOCKERFILE','DOCKERHUB','URL','GIT','LOCAL_IMAGE')

DICT_PKL = Path("./simplej/dict.pkl")

