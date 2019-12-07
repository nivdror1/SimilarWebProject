from django.test import TestCase
from .tasks import process_a_single_csv_file, process_sessions, save_unique_urls, save_num_of_sessions, find_and_save_medians, find_median
from .models import UniqueSiteTable, NumSessionTable, SiteMedianTable
from .session import Session

class FileProcessingTestCase(TestCase):

    def setUp(self):
        self.csv_files = ['C:\\Users\\user\\Downloads\\test_same_session.csv.txt',
                          'C:\\Users\\user\\Downloads\\test_differ_session.csv.txt',
                          'C:\\Users\\user\\Downloads\\test_differ_visitor.csv.txt',
                          'C:\\Users\\user\\Downloads\\test_differ_site.csv.txt']
        self.session = {}
        self.session_info = []
        self.unique_urls = {}
        self.num_of_sessions_dict = {}
        self.sessions_length = {}

    def test_same_session(self):
        process_a_single_csv_file(self.csv_files[0], self.session, self.session_info)
        s1 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        s1.update_timestamp('1347910322')

        self.assertEqual(self.session['visitor_8335']['www.s_9.com'].start_timestamp, s1.start_timestamp)
        self.assertEqual(self.session['visitor_8335']['www.s_9.com'].end_timestamp, s1.end_timestamp)
        self.assertNotEqual(self.session['visitor_8335']['www.s_9.com'].get_length(), 0)

    def test_different_session(self):
        process_a_single_csv_file(self.csv_files[1], self.session, self.session_info)
        s1 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        s2 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        s2.update_timestamp('1347912322')

        self.assertNotEqual(self.session['visitor_8335']['www.s_9.com'].start_timestamp, s2.start_timestamp)
        self.assertEqual(self.session['visitor_8335']['www.s_9.com'].end_timestamp, s2.end_timestamp)
        self.assertEqual(self.session['visitor_8335']['www.s_9.com'].get_length(), 0)
        self.assertEqual(self.session_info[0].site, s1.site)
        self.assertEqual(self.session_info[0].visitor, s1.visitor)
        self.assertEqual(self.session_info[0].get_length(), 0)

    def test_different_visitor(self):
        process_a_single_csv_file(self.csv_files[2], self.session, self.session_info)
        s1 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        s2 = Session('visitor_8333', 'www.s_9.com', '1347909821')

        self.assertEqual(self.session['visitor_8335']['www.s_9.com'].visitor, s1.visitor)
        self.assertEqual(self.session['visitor_8333']['www.s_9.com'].visitor, s2.visitor)

    def test_different_site(self):
        process_a_single_csv_file(self.csv_files[3], self.session, self.session_info)
        s1 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        s2 = Session('visitor_8335', 'www.s_10.com', '1347909821')

        self.assertEqual(self.session['visitor_8335']['www.s_9.com'].site, s1.site)
        self.assertEqual(self.session['visitor_8335']['www.s_10.com'].site, s2.site)

    def test_process_sessions(self):
        s1 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        s2 = Session('visitor_8335', 'www.s_10.com', '1347909821')
        sessions_info = [s1, s2]
        process_sessions(sessions_info, self.unique_urls, self.num_of_sessions_dict, self.sessions_length)

        urls = {'www.s_9.com', 'www.s_10.com'}
        self.assertEqual(self.unique_urls['visitor_8335'], urls)
        self.assertEqual(self.num_of_sessions_dict['www.s_9.com'], 1)
        self.assertEqual(self.sessions_length['www.s_9.com'], [0])

    def test_increase_num_of_sessions(self):
        s1 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        s2 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        sessions_info = [s1, s2]
        process_sessions(sessions_info, self.unique_urls, self.num_of_sessions_dict, self.sessions_length)

        self.assertEqual(self.num_of_sessions_dict['www.s_9.com'], 2)

    def test_multiple_length(self):
        s1 = Session('visitor_8335', 'www.s_9.com', '1347909821')
        s2 = Session('visitor_8333', 'www.s_9.com', '1347909821')
        sessions_info = [s1, s2]
        process_sessions(sessions_info, self.unique_urls, self.num_of_sessions_dict, self.sessions_length)

        self.assertEqual(self.sessions_length['www.s_9.com'], [0, 0])

    def test_save_unique_urls(self):
        urls = {'visitor_8335': {'www.s_9.com', 'www.s_10.com'}}
        save_unique_urls(urls)
        self.assertEqual(UniqueSiteTable.objects.get(visitor='visitor_8335').num_of_unique_sites, 2)

    def test_save_num_of_session(self):
        num_of_session_dict = {'www.s_9.com': 5}
        save_num_of_sessions(num_of_session_dict)
        self.assertEqual(NumSessionTable.objects.get(site='www.s_9.com').numSession, 5)

    def test_find_median_odd_list(self):
        session_length = [1,5,2,4,3]
        median = find_median(session_length)
        self.assertEqual(median, 3)

    def test_find_median_even_list(self):
        session_length = [1,2,4,3]
        median = find_median(session_length)
        self.assertEqual(median, 2.5)

    def test_find_and_save_medians(self):
        length_dict = {'www.s_9.com': [1,5,2,4,3]}
        find_and_save_medians(length_dict)
        self.assertEqual(SiteMedianTable.objects.get(site='www.s_9.com').median, 3.00)