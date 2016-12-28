import inspect, os
import imp
from simple_jupyter_workflow.constants import SOURCES

# specify source of image
# choices are DOCKERFILE, DOCKERHUB, URL, LOCAL_IMAGE
#source = SOURCES.DOCKERHUB
source = SOURCES.GIT

if source == SOURCES.DOCKERHUB:
    #name of image from Docker Hub
    image_name = 'eipdev/alpine-jupyter-notebook'
    image_tag = 'latest'


if source == SOURCES.DOCKERFILE:
    pass


if source == SOURCES.URL:
   url = 'https://gist.githubusercontent.com/dfd/ab87a3d7e232d271a02dddea71af416b/raw/0bc9a001386ee1c555c0b7bc3d90a2266206eab5/Dockerfile' 


if source == SOURCES.GIT:
    git_url = 'https://github.com/CognitiveScale/alpine-jupyter'
    df_name = 'Dockerfile'

if source == SOURCES.LOCAL_IMAGE:
    pass


# define directory in container to bind to local notebooks directory
#dir_to_mount = '/home/jovyan/.jupyter/' # for Dockerfile
dir_to_mount = '/opt/notebook/' # for 'eipdev/alpine-jupyter-notebook
