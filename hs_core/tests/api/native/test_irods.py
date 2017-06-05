import os

from django.contrib.auth.models import Group
from django.test import TestCase

from hs_core import hydroshare
from hs_core.testing import MockIRODSTestCaseMixin

from pprint import pprint


class TestTickets(MockIRODSTestCaseMixin, TestCase):
    def setUp(self):
        super(TestTickets, self).setUp()
        self.group, _ = Group.objects.get_or_create(name='Hydroshare Author')
        self.user = hydroshare.create_account(
            'user1@nowhere.com',
            username='user1',
            first_name='Creator_FirstName',
            last_name='Creator_LastName',
            superuser=False,
            groups=[]
        )

        self.res = hydroshare.create_resource(
            'GenericResource',
            self.user,
            'test resource',
        )
        self.res.save()

        # create a file
        self.test_file_name1 = 'file1.txt'
        self.file_name_list = [self.test_file_name1, ]

        # put predictable contents into the file
        test_file = open(self.test_file_name1, 'w')
        test_file.write("Test text file in file1.txt")
        test_file.close()

        self.test_file_1 = open(self.test_file_name1, 'r')

        # add one file to the resource: necessary so data/contents is created.
        hydroshare.add_resource_files(self.res.short_id, self.test_file_1)

    def tearDown(self):
        super(TestTickets, self).tearDown()
        self.test_file_1.close()
        os.remove(self.test_file_1.name)

    def test_get_file_ticket(self):
        file = self.res.files.all()[0]
        ticket = file.create_ticket(self.user)
        attrs = self.res.list_ticket(ticket)
        self.assertTrue(attrs['data collection'].endswith(self.res.file_path)) 
        self.assertEqual(file.short_path, attrs['data-object name']) 
        self.res.delete_ticket(ticket) 

    def test_get_dir_ticket(self): 
        ticket = self.res.create_ticket(self.user, self.res.file_path)
        attrs = self.res.list_ticket(ticket)
        self.assertTrue(attrs['collection name'].endswith(self.res.file_path)) 
        self.res.delete_ticket(ticket) 
