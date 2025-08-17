INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crm',
    'graphene_django',
    'django_filters',
]

GRAPHENE = {
    'SCHEMA': 'graphql_crm.schema.schema',
}

# ...other settings as needed...
