import ApiManager
import DbManager
import time


id = '_id'

def main():
    nmb_postings = update_db()
    report(nmb_postings)


def update_db():
    # Get the postings from the API
    new_postings = ApiManager.get_postings(f'https://api.smartrecruiters.com/v1/companies/Eurofins/postings')

    # Get the ids of posting already inserted in the database
    postings_ids = []
    for posting in DbManager.find_all():
        postings_ids.append(posting[id])

    postings_to_delete = postings_ids
    postings_to_insert = []

    prev_time = 0
    nmb_requests = 0

    for posting in new_postings:
        start = time.time()
        # Get the details of a posting
        posting_document = ApiManager.get_posting_details(posting).document
        nmb_requests += 1
        if posting_document != None:
            # Check if a posting is already in the database
            if posting['id'] in postings_ids:
                # If yes, update it and remove its id from the postings_to_delete list because it is still an available job
                if DbManager.update({id: posting[id]}, posting_document):
                    print(f'Posting with id {posting[id]} updated.\n')
                else:
                    print(f'Posting with id {posting[id]} could not be updated.\n')
                postings_to_delete.remove(posting[id])
            else:
                # Otherwise add it to the postings to be inserted in the database
                postings_to_insert.append(posting_document)
        end = time.time()
        current_time = end - start + prev_time
        # Check if the number of requests sent does not exceed the number allowed by the API (10 per second)
        if nmb_requests == 10 and current_time < 1:
            print('waiting... ', 1.1-current_time)
            time.sleep(1.1-current_time)
            prev_time = 0
            nmb_requests = 0
        elif current_time >= 1:
            prev_time = current_time-1
            nmb_requests = 1
        else:
            prev_time = current_time

    # Insert the postings in the database
    inserted_postings = DbManager.insert_all(postings_to_insert)
    # Check if the postings were correctly inserted
    if inserted_postings.acknowledged:
        print(f'{inserted_postings.inserted_ids.len} postings inserted.\n')
    else:
        print(f'Posting with ids {inserted_postings.inserted_ids} could not be inserted.\n')

    # Delete the postings that are not available anymore
    for posting_id in postings_to_delete:
        if DbManager.delete({id: posting_id}):
            print(f'Posting with id {posting_id} deleted.\n')
        else:
            print(f'Posting with id {posting_id} could not be deleted.\n')

    return len(new_postings)


def report(nmb_postings):
    print(f'{nmb_postings} postings were retrieved from the API')
    posting_by_contract_type = list(DbManager.collection.aggregate([{"$group": {"_id": "$contract_type", "count": {"$sum": 1}}}]))
    posting_by_location = list(DbManager.collection.aggregate([{"$group": {"_id": "$location", "count": {"$sum": 1}}}]))
    for type in posting_by_contract_type:
        if len(type[id]) < 2:
            print(f'There are {type["count"]} offers with no contract type specified')
        else:
            print(f'There are {type["count"]} offers of {type[id]} type')
    for city in posting_by_location:
        if city["count"] == 1:
            print(f'There is {city["count"]} offer in {city[id]}')
        else:
            print(f'There are {city["count"]} offers in {city[id]}')

main()
