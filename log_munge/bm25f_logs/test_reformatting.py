import re
from collections import namedtuple

# test to ensure the output of the transmute_logs.py script for
# machine-readable logging is in fact conformant to the Apache Combined
# logging Format

# TODO: Refactor as regex hash

TestResponse = namedtuple('TestMessage', 'passed message')

def test_reference_document():
    with open('sample_log.txt') as sample:
        test_results = []
        for line in sample.readlines():
            test_results.extend(test_log_entry(line))
        output_test_results(test_results)

def test_reformatted_document(session_id):
    filename = "session_" + session_id + ".txt"
    with open("output/for_machines/" + filename) as rfd:
        test_results = []
        for line in rfd.readlines():
            test_results.extend(test_log_entry(line))
        output_test_results(test_results)

def test_log_entry(entry):
    entry_responses = []
    logbits = split_log_line(entry)
    try:
        (client_ip, user_id, user_name, timestamp, request_line, status_code, response_size, referer, user_agent) = logbits
        entry_responses.append(TestResponse(True, "Correct number of fields found in log line"))
        entry_responses.append(test_client_ip(client_ip))
        entry_responses.append(test_user_id(user_id))
        entry_responses.append(test_user_name(user_name))
        entry_responses.append(test_timestamp(timestamp))
        entry_responses.append(test_request_line(request_line))
        entry_responses.append(test_status_code(status_code))
        entry_responses.append(test_response_size(response_size))
        entry_responses.append(test_referer(referer))
        entry_responses.append(test_user_agent(user_agent))
    except ValueError as ve:
        return [TestResponse(False, str(ve))]
    return entry_responses

def output_test_results(test_results):
    failure_count = 0
    for response in test_results:
        # for now we just write to STDOUT
        msg = ""
        if(response.passed == True):
            pass
        else:
            msg = "Test failed: " + response.message
            failure_count += 1
            print(msg)
    if(failure_count > 0):
        print("TEST SUITE FAILED WITH " + str(failure_count) + " FAILURES")
    else:
        print("TEST SUITE PASSED")

def split_log_line(log_line):
    log_line = log_line.strip()
    return re.split("\s(?=[[0-9\"-])", log_line, maxsplit=8)

def test_client_ip(ip_address):
    if(re.match("\A(\d{1,3}\.){3}(\d{1,3})$", ip_address)):
        return TestResponse(True, "IP address ok")
    else:
        return TestResponse(False, "IP address " + str(ip_address) + " malformed")

def test_user_id(user_id):
    if(user_id == "-"): return TestResponse(True, "User ID spoof value supplied")
    return TestResponse(False, "User ID value should be spoofed")

def test_user_name(user_name):
    if(user_name == "-"): return TestResponse(True, "User name spoof value supplied")
    return TestResponse(False, "User name value should be spoofed")

def test_timestamp(timestamp):
    if(re.match("\A\[\d{2}\/[A-Z][a-z][a-z]\/\d{4}:\d{2}:\d{2}:\d{2} \+\d{4}\]$", timestamp)):
        return TestResponse(True, "Timestamp correctly formatted")
    else:
        return TestResponse(False, "Timestamp (" + timestamp + ") incorrectly formatted")

def test_request_line(request_line):
    if(re.match("\A\"GET \/.+ HTTP\/\d\.\d\"", request_line)):
        return TestResponse(True, "Request line correctly formatted")
    else:
        return TestResponse(False, "Request line " + request_line + " incorrectly formatted")

def test_status_code(status_code):
    if(re.match("\A\d{3}$", status_code)):
        return TestResponse(True, "Status code correctly formatted")
    else:
        return TestResponse(False, "Status code " + str(status_code) + " incorectly formatted")

def test_response_size(response_size):
    if(re.match("\A\d+$", response_size)):
        return TestResponse(True, "Response size correctly formatted")
    else:
        return TestResponse(False, "Response size " + str(response_size) + " incorectly formatted")

def test_referer(referer):
    if(re.match("\A\".+\"$", referer)):
        return TestResponse(True, "Referer correctly formatted or spoofed")
    else:
        return TestResponse(False, "Referer " + str(referer) + " incorectly formatted")

def test_user_agent(user_agent):
    if(re.match("\A\".+\"$", user_agent)):
        return TestResponse(True, "User agent correctly formatted or spoofed")
    else:
        return TestResponse(False, "User agent " + str(user_agent) + " incorectly formatted")


test_reference_document()
test_sessions = ["208528ae0322dbb05aa11a6829013274", "c2d06c0cde39879aa219117aefd72789", "292a2eec8c1146ea7f99070db795eabe", "61d793c6b93a9eb84d1b8d56b9cb25cb", "a83c34b998cff82dafda10fc7f7e344a"]
[test_reformatted_document(session) for session in test_sessions]
