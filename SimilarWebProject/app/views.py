from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import HttpResponse
import json
from .tasks import process_multiple_csv_files
from .models import UniqueSiteTable, NumSessionTable, SiteMedianTable
from django.core.exceptions import ObjectDoesNotExist


FILES_LIST_ARGUMENT = "files_list"


def validate_content(content):
    """
    Validate the content of the request body - check if the are file names in the request body
    :param content: The request body
    :return: Boolean
    """
    if FILES_LIST_ARGUMENT in content:
        if len(content[FILES_LIST_ARGUMENT]) > 0:
            return True

    return False


@csrf_exempt
def process_files_view(request):
    """
    Check if the request is valid if so process all of the csv files
    :param request: HTTP request contains the list of the csv files
    :return: HTTP response
    """
    if request.method == 'POST':
        body_unicode = request.body.decode('utf-8')
        content = json.loads(body_unicode)

        if validate_content(content):
            process_multiple_csv_files.apply_async([content[FILES_LIST_ARGUMENT]])
            return HttpResponse(status=200)

    return HttpResponse(status=400)


def get_unique_urls_view(request):
    """
    Get the visitor from the url parameter and then query the UniqueSiteTable in the DB for that record.
    :param request: HTTP request contains the visitor to search
    :return: HTTP response
    """
    if request.method == 'GET':
        visitor = request.GET['visitor']
        try:
            unique_sites = UniqueSiteTable.objects.get(visitor=visitor)
        except ObjectDoesNotExist:
            return HttpResponse("No such visitor")
        return HttpResponse("The num of unique sites the {} has visited is {}.".format(visitor, unique_sites.num_of_unique_sites))

    return HttpResponse(status=400)


def get_num_of_session_view(request):
    """
    Get the site from the url parameter and then query the NumSessionTable in the DB for that record.
    :param request: HTTP request contains the site to search
    :return: HTTP response
    """
    if request.method == 'GET':
        site = request.GET['site']
        try:
            site_record = NumSessionTable.objects.get(site=site)
        except ObjectDoesNotExist:
            return HttpResponse("No such site")
        return HttpResponse("Num sessions for site {} = {}.".format(site, site_record.numSession))

    return HttpResponse(status=400)


def get_median_per_site_view(request):
    """
    Get the site from the url parameter and then query the SiteMedianTable in the DB for that record.
    :param request: HTTP request contains the site to search
    :return: HTTP response
    """
    if request.method == 'GET':
        site = request.GET['site']
        try:
            site_record = SiteMedianTable.objects.get(site=site)
        except ObjectDoesNotExist:
            return HttpResponse("No such site")
        return HttpResponse("The median for the site {} is {}.".format(site, site_record.median))

    return HttpResponse(status=400)