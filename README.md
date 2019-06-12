# Cockroach DB backend for Django 2.2

This is an initial attempt at a backend for Django 2.2. You can install it with the following command: 

`pip install .`

You then can use this by putting the following in your `settings.py` for your site: 

```
DATABASES = {
    'default': {
        'NAME': 'django',
        'USER': 'root',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': '26257',
        'ENGINE': 'cockroach.django',
    }
}

```
