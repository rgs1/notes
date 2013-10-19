#!/usr/bin/python

import time

def run_tests(available_methods):
    passed = failed = 0

    for m in available_methods:
        result = ''
        start = time.time()
        print "\n* Starting %s" % (m.__name__)
        try:
            m()
            passed += 1
            result = "\033[92mpassed\033[0m"
        except Exception, ex:
            result = "\033[91mfailed\033[0m: %s" % (str(ex))
            failed += 1

        print "* Finished %s, result = %s  (%s)\n" % \
            (m.__name__, result, time.time() - start)

    print "Total passed = %d, failed = %d" % (passed, failed)
