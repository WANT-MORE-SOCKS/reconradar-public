# Reconradar
Built for Junction 2025.

## Required packages:
`pip install django markdown google-genai`

## To start using:
Create the file `config.json` (see `config.json.example`)
You will need a Google Gemini API key.
You will also need to generate a Django secret key:
```python
from django.core.management.utils import get_random_secret_key
get_random_secret_key()
```

## Run for testing:
Initiliaze the database:

`python reconradar/manage.py makemigrations assessor`

`python reconradar/manage.py migrate assessor`

Start server:

`python reconradar/manage.py runserver`

## Deployment:
[How to Deploy | Django Documentation](https://docs.djangoproject.com/en/5.2/howto/deployment/)
