# -*- coding: utf-8  -*-
try:
    from urlibe.parse import urlunparse
except ImportError:
    from urlparse import urlunparse  # noqa


def build_dsn(scheme='postgres', hostname='localhost', port=5432, path='', username=None, password=None):
    netloc = hostname or 'localhost'
    if port:
        netloc = "{0}:{1}".format(netloc, port)
    if username and password:
        netloc = "{0}:{1}@{2}".format(username, password, netloc)
    if username and not password:
        netloc = "{0}@{1}".format(username, netloc)
    return urlunparse((scheme, netloc, path, None, None, None))
