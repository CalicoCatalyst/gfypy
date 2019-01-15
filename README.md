# GfyPy

GfyCat API that supports authentication. Only supports file uploads at the moment. PRs welcome

Usage:

```
>>> from gfypy import gfycat

>>> client = gfycat.GfyCatClient(client_id,client_secret,username,password)


>>> gfycat = client.upload_file(filename, title="Title", desc="Description", noMd5 = True, private = True)

>>> print(gfycat.url)

>>> 'http://gfycat.com/{uid}'

