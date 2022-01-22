"""
Author: Amelia Wietting
Date: 20220119
"""
import argparse
import os
from project_earth.projectEarth import projectEarth
from project_earth.projectEarth import apiType

parser = argparse.ArgumentParser(
    description='Demo for downloading images from NASA API')
parser.add_argument('-a', '--action', help='foo help', default=None)
args = vars(parser.parse_args())

# Demo of what it looks like to have handling for not inputing an api type
# This allows for adding additional apis to this project

# none_type_project = projectEarth()

# Now we know we can use EPICDSCOVR, let's focus on that for a moment and make our initial object
# Next let's look at the API to see what is supported: api.nasa.gov
# epic_dscovr = projectEarth(apiType.EPICDSCOVR)

# Oh an error, that's simple enough to fix,
# we need to set our environment variable for our nasa api token
# It's easy to sign up for a key, can go do so right now
os.environ['NASA_API_TOKEN'] = 'DEMO_KEY'
epic_dscovr = projectEarth(apiType.EPICDSCOVR)

if args['action'] is not None:
    if args['action'] == 'index':
        epic_dscovr.index()
    if args['action'] == 'download':
        epic_dscovr.download_epic_dscovr_files()
    if args['action'] == 'video':
        epic_dscovr.make_epic_dscovr_video()
else:
    epic_dscovr.index()
    epic_dscovr.download_epic_dscovr_files()
    epic_dscovr.make_epic_dscovr_video()
