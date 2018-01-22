find .. -name '*.pyc' | xargs rm -f
find .. -name 'setup.py' | xargs rm -f
find .. -name 'data_utf8.json' | xargs rm -f
find .. -name 'data_bak' | xargs rm -fr
find .. -name 'scrapyd_log' | xargs rm -fr
find .. -name 'build' | xargs rm -fr
find .. -name 'project.egg-info' | xargs rm -fr


