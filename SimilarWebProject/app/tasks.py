from __future__ import absolute_import, unicode_literals
from celery import shared_task
import os
import csv
from .pageView import PageView
from .session import Session
from .models import UniqueSiteTable, NumSessionTable, SiteMedianTable
import math
import copy


def update_session(page_view, sessions, sessions_info):
    """
    check if is it the same session then update the timestamp, otherwise append the former session into session_info list
    and create a new session
    :param page_view: The current page view object
    param sessions: A dict of sessions objects that are on going in this format {visitor: {site: Session}}
    :param sessions_info: A List of ended sessions
    :return:
    """
    cur_session = sessions[page_view.visitor][page_view.site]

    if cur_session.same_session(page_view.timestamp):
        cur_session.update_timestamp(page_view.timestamp)
    else:
        sessions_info.append(copy.deepcopy(cur_session))
        sessions[page_view.visitor][page_view.site] = Session(page_view.visitor, page_view.site,
                                                                  page_view.timestamp)


def process_page_view(page_view, sessions, sessions_info):
    """
    Check if a new session need to be added or modified
    :param page_view: The current page view object
    :param sessions: A dict of sessions objects that are on going in this format {visitor: {site: Session}}
    :param sessions_info: A List of ended sessions
    """

    # Check if a new session need to be added or modified
    if page_view.visitor in sessions:
        if page_view.site in sessions[page_view.visitor]:
            # update the session
            update_session(page_view, sessions, sessions_info)

        else:
            # Create a new session for the visitor and site
            sessions[page_view.visitor][page_view.site] = Session(page_view.visitor, page_view.site, page_view.timestamp)
    else:
        # Create a new session for the visitor and site
        site_session_dict = {page_view.site: Session(page_view.visitor, page_view.site, page_view.timestamp)}
        sessions[page_view.visitor] = site_session_dict


def process_a_single_csv_file(csv_file, sessions, sessions_info):
    """
    Read the csv file then process the page views in it into sessions
    :param csv_file: A string representing the path to the file
    :param sessions: A dict of sessions objects that are on going in this format {visitor: {site: Session}}
    :param sessions_info: A List of ended sessions
    """

    if os.path.isfile(csv_file):

        with open(csv_file,'r') as csv_file:

            csv_reader = csv.reader(csv_file)

            for row in csv_reader:
                # Create a PageView object
                page_view = PageView(row[0], row[1], row[2], row[3])
                # process the page view
                process_page_view(page_view, sessions, sessions_info)


def add_a_unique_url(session_info, unique_urls):
    """
    check if the current site wasn't visited by the visitor already is so add it to the set
    :param session_info: The session object
    :param unique_urls: A dict which contains the following info {visitor: set(sites)}
    """
    if session_info.visitor in unique_urls:
        if session_info.site not in unique_urls[session_info.visitor]:
            unique_urls[session_info.visitor].add(session_info.site)
    else:
        unique_urls[session_info.visitor] = {session_info.site}


def increase_num_of_sessions(site, num_of_sessions):
    """
    Increase the sessions counter for the specific site
    :param site: The current site
    :param num_of_sessions: A dict which contains the following info {site: sessions number}
    """
    if site in num_of_sessions:
        num_of_sessions[site] += 1
    else:
        num_of_sessions[site] = 1


def add_session_length(session_info, sessions_length):
    """
    Add the session length to the list of the specific site
    :param session_info: The session object
    :param sessions_length: A dict which contains the following info {site: [sessions length]}
    """
    if session_info.site in sessions_length:
        sessions_length[session_info.site].append(session_info.get_length())
    else:
        sessions_length[session_info.site] = [session_info.get_length()]


def process_sessions(sessions_info, unique_urls, num_of_sessions_dict, sessions_length):
    """
    Process sessions into unique_urls, num_of_sessions_dict, sessions_length
    :param sessions_info: A list of sessions objects
    :param unique_urls: A dict which contains the following info {visitor: set(sites)}
    :param num_of_sessions_dict: A dict which contains the following info {site: sessions number}
    :param sessions_length: A dict which contains the following info {site: [sessions length]}
    """
    for session_info in sessions_info:

        # check if the current site wasn't visited by the visitor already is so add it to the set
        add_a_unique_url(session_info, unique_urls)

        # Increase the sessions counter for the specific site
        increase_num_of_sessions(session_info.site, num_of_sessions_dict)

        # Add the session length to the list of the specific site
        add_session_length(session_info, sessions_length)


def save_unique_urls(unique_urls):
    """
    Save the number of unique urls for each visitor
    :param unique_urls: A dict which contains the following info {visitor: set(sites)}
    """
    for visitor, set_urls in unique_urls.items():
        unique_site = UniqueSiteTable(visitor=visitor, num_of_unique_sites=len(set_urls))
        unique_site.save()


def save_num_of_sessions(num_of_sessions_dict):
    """
    Save the num of sessions for each site
    :param num_of_sessions_dict: A dict which contains the following info {site: sessions number}
    """
    for site, num in num_of_sessions_dict.items():
        site_sessions = NumSessionTable(site=site, numSession=num)
        site_sessions.save()


def find_median(length_arr):
    """
    Find the sessions median for a site
    :param length_arr: An list that contains the sessions length
    :return: The median
    """
    # sort the lengths of the sessions
    length_arr = sorted(length_arr)
    median = 0

    # Find the median
    if len(length_arr) % 2 != 0:
        index = math.floor(len(length_arr) / 2)
        median = length_arr[index]
    else:
        half = len(length_arr) // 2
        median = (length_arr[half] + length_arr[half - 1]) / 2

    return median


def find_and_save_medians(sessions_length):
    """
    find and save the median for each site
    :param sessions_length: A dict which contains the following info {site: [sessions length]}
    """
    for site, length_arr in sessions_length.items():

        median = find_median(length_arr)
        median_per_site = SiteMedianTable(site=site, median=median)
        median_per_site.save()


def save_info_to_db(unique_urls, num_of_sessions_dict, sessions_length):
    """
    Save the info gathered in the data structure into the following tables in the DB:
    UniqueSiteTable, SiteMedianTable, NumSessionTable
    :param unique_urls: A dict which contains the following info {visitor: set(sites)}
    :param num_of_sessions_dict: A dict which contains the following info {site: sessions number}
    :param sessions_length: A dict which contains the following info {site: [sessions length]}
    """
    # Save the number of unique urls that the visitors has entered
    save_unique_urls(unique_urls)

    # Save the number of sessions made to a site
    save_num_of_sessions(num_of_sessions_dict)

    # find the session length median for each site and save it
    find_and_save_medians(sessions_length)


def append_remaining_sessions(sessions, sessions_info):
    """
    Append the remaining sessions into the session_info list
    :param sessions: A dict of sessions objects that are on going in this format {visitor: {site: Session}}
    :param sessions_info: A List of ended sessions
    """
    for visitor, sites_sessions in sessions.items():
        for site, cur_session in sites_sessions.items():
            sessions_info.append(cur_session)


@shared_task
def process_multiple_csv_files(files):
    """
    process multiple csv files. for each csv file process the page view into session.
    than process the session into useful data structure and in the end save them into the DB
    :param files: An array of strings representing the path of the files
    """

    sessions = {}
    sessions_info = []
    unique_urls = {}
    num_of_sessions_dict = {}
    sessions_length = {}

    for csv_file in files:
        process_a_single_csv_file(csv_file, sessions, sessions_info)

    append_remaining_sessions(sessions, sessions_info)

    process_sessions(sessions_info, unique_urls, num_of_sessions_dict, sessions_length)

    save_info_to_db(unique_urls, num_of_sessions_dict, sessions_length)