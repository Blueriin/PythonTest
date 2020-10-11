import requests
import time
import Posting

content = "content"
totalFound = 'totalFound'
limit = 'limit'
ref = 'ref'


def get_postings(url):
    """
    Return a list of json postings
    Parameters
    ----------
    url : str
        The url to get the postings
    """
    postings = []
    response = requests.get(url)
    # If the request is valid
    if response.status_code == requests.codes.ok:
        response = response.json()
        postings.extend(response[content])

        # Calculate the ratio of the number of postings obtained divided by the total number of postings,
        # in order to get all the postings
        max_elements = response[limit]
        ratio = response[totalFound] // max_elements

        time.sleep(1)
        prev_time = 0
        nmb_requests = 0

        for i in range(1, ratio + 1):
            start = time.time()
            payload = {'offset': f'{i * max_elements}'}
            # Get the next postings
            response = requests.get(url, params=payload)
            nmb_requests += 1
            if response.status_code == requests.codes.ok:
                # Add the new postings to the list
                postings.extend(response.json()[content])
            else:
                print("request error for request number ", i)
            end = time.time()
            current_time = end - start + prev_time
            # Check if the number of requests sent does not exceed the number allowed by the API (10 per second)
            if nmb_requests == 10 and current_time < 1:
                time.sleep(1.1 - current_time)
                prev_time = 0
                nmb_requests = 0
            elif current_time >= 1:
                prev_time = current_time-1
                nmb_requests = 1
            else:
                prev_time = current_time
    else:
        print("request error")
    return postings


def get_posting_details(posting):
    """
    Get details about one posting and returns a Posting object
    Parameters
    ----------
    posting : dict
        The posting from which the details are wanted
    """
    response = requests.get(posting[ref])
    # If the request is valid
    if response.status_code == requests.codes.ok:
        response = response.json()
        # Get the location city
        location = response['location']['city']
        # Get the contract type
        contract_type = response['customField']['1']['valueLabel']
        '''for element in response['customField']:
            if element['fieldLabel'] == "Contract Type":
                contract_type = element['valueLabel']'''
        # Format the description
        description = (f"{response['jobAd']['sections']['companyDescription']['title']}\n" +
                       f"{response['jobAd']['sections']['companyDescription']['text']}\n" +
                       f"{response['jobAd']['sections']['jobDescription']['title']}\n" +
                       f"{response['jobAd']['sections']['jobDescription']['text']}\n" +
                       f"{response['jobAd']['sections']['qualifications']['title']}\n" +
                       f"{response['jobAd']['sections']['qualifications']['text']}\n" +
                       f"{response['jobAd']['sections']['additionalInformation']['title']}\n" +
                       f"{response['jobAd']['sections']['additionalInformation']['text']}\n")

        return Posting.Post(response['id'], response['name'], location, contract_type, response['applyUrl'],
                            description)
    else:
        print(f'Request error for ref {posting[ref]}. The details could not be obtained')
        return None
