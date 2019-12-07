# SimilarWebProject

1) Description of my solution:

    I have built a backend server in Python using Django.

    On initialization the server will receive the request containing the paths to the csv files.
    Here is main logic of server, for each csv file it will transform the information for page views to session.
    Then it will process the sessions into data structures and then save them into the db.

    Afterwards, the server will be able to receive and respond properly to all three queries quickly.

2)

    In order to set up the project you first to need to install the following:
    Django Framework package,
    RabbitMQ,
    Celery,
    Postgresql - you need to create a DB called similarweb_db
    Postman

    open a cmd and write the following opartions:
        cd <relative_path>/SimilarWebProject/SimilarWebProject
        python manage.py makemigrations
        python manage.py migrate
        python manage.py runserver

    open another cmd and write the following opartions:
        cd <relative_path>/SimilarWebProject/SimilarWebProject
        celery -A SimilarWebProject worker --loglevel=INFO

    enter Postman and open a new request:
        to process the csv files : set the method to POST and write this in the url "http://127.0.0.1:8000/process-files/"
                                  with a body of {"files-list": [<csv_file_path>]}

        to query the unique urls per visitor: set the method to GET and write this in the url "http://127.0.0.1:8000/unique-urls?visitor=<visitor>"
        to query the sessions number per site: set the method to GET and write this in the url "http://127.0.0.1:8000/num-sessions?site=<site>"
        to query the sessions median per site: set the method to GET and write this in the url "http://127.0.0.1:8000/median?site=<site>"


3)

    In order to support scale I would have make a cluster of servers that
    each would access to the db (perhaps even make a few redundancy DB).
    Even though the queries are fast I would have included a cache to store the lastest queries.

    Now in order to make the initialization scaleable I have would have increased the number celery workers so the process
    will be split on a few processes.

4) init = time complexity is O(mlog(m)) where m is number of sessions. this comes from the sorting a the list in my search
   for the sessions median in case the session number is huge.
   the space complexity on the RAM is O(m) where m is number of sessions.
   the space complexity on the DB is O(j + k) where j is site and k is the number of visitors.

5) I have tested a number functions in tests.py and did a few integration tests with the postman
