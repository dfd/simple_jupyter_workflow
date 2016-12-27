from constants import *
import inspect, os


# specify source of image
# choices are DOCKERFILE, DOCKERHUB, URL, LOCAL_IMAGE
#source = SOURCES.DOCKERHUB
source = SOURCES.DOCKERFILE

if source == SOURCES.DOCKERHUB:
    #name of image from Docker Hub
    image_name = 'eipdev/alpine-jupyter-notebook'
    image_tag = 'latest'


if source == SOURCES.DOCKERFILE:
    pass


if source == SOURCES.URL:
    pass


if source == SOURCES.LOCAL_IMAGE:
    pass


# define directory in container to bind to local notebooks directory
dir_to_mount = '/home/jovyan/.jupyter/' # for Dockerfile
#dir_to_mount = '/opt/notebook/' # for 'eipdev/alpine-jupyter-notebook
