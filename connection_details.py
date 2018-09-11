import os
import pymongo


def get_uri():
    MONGODB_URI = ('mongodb://admin:c00k800k32-@ds251332.mlab.com:51332/cookbook')
    return MONGODB_URI


def get_dbs_name():
    DBS_NAME = "cookbook"
    return DBS_NAME
