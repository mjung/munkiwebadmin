from django.shortcuts import render

from django.http import HttpResponse, HttpResponseBadRequest

from django.template import RequestContext, loader

from .models import JSSComputerAttributeMapping

from django.contrib.auth.decorators import login_required, permission_required, user_passes_test

from guardian.shortcuts import get_objects_for_user

from django.core.exceptions import ObjectDoesNotExist

from .models import JSSUser
from .decorators import jss_user_required

from manifests.models import Manifest

import jss
from django.conf import settings
from lxml import etree


import re

# Create your views here.

@login_required
@jss_user_required
def index(request):
     
    sites = get_objects_for_user(request.user, 'jssmanifests.can_view_jsssite')

    mappings = JSSComputerAttributeMapping.objects.filter(jsssite__exact=sites)

    template = loader.get_template('jssmanifests/index.html')
    context  = RequestContext(request, { 'mappings': mappings, 'sites': sites })

    return HttpResponse( template.render(context) )
