# import pytest
# import sys
# from os import environ, path
# from datetime import datetime, timedelta
# from time import sleep

if __name__ == '__main__':
    # leaving the following as a blueprint for how to do this kind of test
    # if 'FAST_REPORT_START_TIME' in environ.keys():
    #     start_time = datetime.strptime(environ['FAST_REPORT_START_TIME'], '%Y-%m-%dT%H:%M:%S')
    #     end_time = start_time + timedelta(minutes=5)
    #     utcnow = datetime.utcnow()
    #     remaining = end_time - utcnow
    #     if remaining > timedelta(seconds=0):
    #         print(f'Waiting for fast-report end: {remaining.total_seconds()}s ...')
    #         sleep(remaining.total_seconds())
    #         check_test = path.join(path.dirname(path.realpath(__file__)), 'tests', 'test_check_fast_report.py')
    #         retcode = pytest.main(['-vs', check_test])
    #         if retcode > 0:
    #             sys.exit(retcode)
    pass