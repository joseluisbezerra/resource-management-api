import json
import yaml

from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import render
from django.conf import settings


def documentation(request):
    if hasattr(settings, 'SWAGGER_YAML_FILE'):
        file = open(settings.SWAGGER_YAML_FILE)
        spec = yaml.safe_load(file.read())

        return render(
            request,
            template_name="utils/swagger-ui.html",
            context={'data': json.dumps(spec)}
        )
    else:
        raise ImproperlyConfigured(
            'You should define SWAGGER_YAML_FILE in your settings'
        )