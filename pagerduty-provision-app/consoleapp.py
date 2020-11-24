from copy import deepcopy
from itertools import product

from pandas import DataFrame

from adaptapp.modules.escalation_policy import get_ep
from adaptapp.modules.file_modifier import create_file
from adaptapp.modules.incident import incident_iter_selected
from adaptapp.modules.service import get_service
from adaptapp.modules.tag import extract_key_value, extract_separators, extract_regex
from adaptapp.modules.validator import is_token_valid, get_subdomain
from adaptapp.modules.datadog_config import get_all_tags

durations = {"1": 30, "2": 60, "3": 90, "4": 120, "5": 150, "6": 180, "7": 210, "8": 240, "9": 270, "10": 300,
             "11": 330, "12": 360, "13": 440, "14": 720, "15": 900, "16": 1080}

integrations = {"1": "datadog", "2": "dynatrace", "3": "nagios", "4": "custom"}


def run_datadog():
    # DD API Keys
    dd_app_key = ''
    dd_api_key = ''

    # Get API Keys from user input
    while True:
        global_key = validating_token('REST API')
        user_key = validating_token('User API')

        if get_subdomain(global_key) == get_subdomain(user_key):
            break
        print("Global key and User key do not belong to the same subdomain.")

    # Get subdomain
    subdomain = get_subdomain(global_key)
    print("API Keys you entered belong to: %s" % subdomain)
    # Get EP by its ID
    ep_object = get_ep(global_key)
    print("You have chosen '%s' as your default escalation policy.\n" % ep_object['summary'])


    tags = get_all_tags(dd_api_key,dd_app_key)
    field_loc = create_file('fields.csv', 'resources', 'console', subdomain)
    DataFrame.from_dict(data=tags, orient='index').transpose().to_csv(field_loc, index=False)
    print("Field data saved in %s" % field_loc)

    tags = tag_extractions(tags)



def run_pagerduty():
    # Get API Keys from user input
    while True:
        global_key = validating_token('REST API')
        user_key = validating_token('User API')

        if get_subdomain(global_key) == get_subdomain(user_key):
            break
        print("Global key and User key do not belong to the same subdomain.")

    # Get subdomain
    subdomain = get_subdomain(global_key)
    print("API Keys you entered belong to: %s" % subdomain)
    # Get EP by its ID
    ep_object = get_ep(global_key)
    print("You have chosen '%s' as your default escalation policy.\n" % ep_object['summary'])

    services = []
    windows = []

    # Get Service ID and Discovery Window
    print("Now enter service ID's that you want to discover. You may enter one by one.")
    while True:
        if not services:
            service_id = input("Service ID: ")
        else:
            service_id = input("Next Service ID (or enter 'next' to move forward): ")

        if service_id.lower() == 'next':
            break

        service = get_service(global_key, service_id)
        if not service:
            print("Invalid Service ID. No Services found. Enter a valid service id.\n")
            continue

        if service_id not in services:
            services.append(service_id)

        print("The last incident occurrence in the selected service'%s': '%s'" % (
            service['summary'], service['last_incident_timestamp']))

        while True:
            disco_window = input("Choose one of the event discovery windows for the service '%s': " + \
                                 "\n(1) 30 \n(2) 60 \n(3) 90 \n(4) 120 \n(5) 150" + \
                                 "\n(6) 180 \n(7) 210 \n(8) 240 \n(9) 270 \n(10) 300 \n(11) 330 \n(12) 360" + \
                                 "\n(13) 440 \n(14) 720 \n(15) 900 \n(16) 1080\nChoice: ")
            if disco_window not in durations.keys():
                print("Incorrect input. Try again.\n")
                continue
            break
        windows.append(disco_window)

    # Get Integration type of discovery
    while True:
        integration_type = input(
            "Choose the dataset type: \n(1) Datadog\n(2) Dynatrace\n(3) Nagios\n(4) Custom Dataset\nChoice: ")
        if integration_type not in ["1", "2", "3", "4"]:
            continue
        break

    incidents = []
    tags = {}

    # Get Incident events
    for i in range(len(services)):
        print("Fetching events data..")
        incidents = incidents + incident_iter_selected(global_key, windows[i], services[i],
                                                       integrations[integration_type], tags)

    # Incident data into CSV - doesn't work due to nested json so far
    # incident_loc = create_file('incidents.csv', 'resources', 'console', subdomain)
    # DataFrame.from_records(data=incidents).transpose().to_csv(incident_loc, index=False)
    # print("Incident data saved in %s" % incident_loc)

    field_loc = create_file('fields.csv', 'resources', 'console', subdomain)
    DataFrame.from_dict(data=tags, orient='index').transpose().to_csv(field_loc, index=False)
    print("Field data saved in %s" % field_loc)

    # For datadog, start from here
    # Tag Extraction Process
    tags = tag_extractions(tags)

    # Update Fields data
    field_loc_v2 = create_file('fields_v2.csv', 'resources', 'console', subdomain)
    DataFrame.from_dict(data=tags, orient='index').transpose().to_csv(field_loc_v2, index=False)
    print("Field data saved in %s" % field_loc_v2)

    print("Set up Service Abstraction..")
    field_abstractions = []
    combo = []
    # print("-----------------\nInstructions\n-----------------\n")
    # print("Step 1: Select a separator between two fields, not longer than 1 char\n")
    # print("Step 2: Select the field you wish to add in \n")
    # print("Step 3: (Optional) Choose prefix and suffix for each field\n")
    # print("Step N+1: Continue to pick other fields, then add\n")
    # print("----------------------------------------------------")

    while True:
        field_len = input("How many fields do you want to add: ")
        if len(field_len) != 1 and field_len not in '12345678':
            print('Invalid input. Try again. Also, do not add more than 9 fields')
            continue
        counter = 0
        current_abstraction = []
        while counter < int(field_len):
            counter += 1
            while True:
                field = input("Enter the field name: ")
                if field not in tags:
                    print("Invalid field name. It doesn't exist in fields.csv file.")
                    continue
                # prefix = input("Enter Prefix or enter nothing: ")
                # suffix = input("Enter Suffix or enter nothing: ")
                current_abstraction.append(field)
                break

        while True:
            sep = input("Enter a separator: ")
            if len(sep) > 1:
                print("Separator can't be more than 1 char long.")
                continue
            break
        current_abstraction.append(sep)
        print("Added the current abstraction.")

        while True:
            decision = input("Do you want to add another abstraction(y/n): ")
            if decision.lower() not in ['y', 'yes', 'n', 'no']:
                print("Invalid input. Try again.")
                continue
            break

        field_abstractions.append(current_abstraction)
        print("Following Abstractions have been selected: ")
        type_count = 0
        for field_abstraction in field_abstractions:
            type_count += 1
            sep_item = field_abstraction[-1]
            str_format = ''
            # print(field_abstraction)
            for i in range(len(field_abstraction) - 1):
                if str_format:
                    str_format += " " + sep_item + " "
                else:
                    str_format += "[type %s] " % str(type_count)
                str_format += field_abstraction[i]
            print(str_format)
        if decision.lower() in ['n', 'no']:
            break
        counter *= 0

    abstractions = {}
    for i in range(len(field_abstractions)):
        abstraction_list = []
        # print(abs_key)
        abs_key = 'type %s:: ' % str(i + 1)
        sep_item = field_abstractions[i][-1]
        valid_abstractions = field_abstractions[i][:-1]
        if len(valid_abstractions) == 1:
            current_abstraction = tags[field_abstractions[i][0]]
            abs_key += field_abstractions[i][0]
            for item in current_abstraction:
                abstraction_list.append(item)
            abstractions[abs_key] = current_abstraction
        else:
            abstraction_combo = []
            for x in range(len(valid_abstractions)):
                abs_key += valid_abstractions[x]
                if x != len(valid_abstractions) - 1:
                    abs_key += ' %s ' % sep_item
                abstraction_combo.append(tags[field_abstractions[i][x]])
            unique_combo = list(product(*abstraction_combo))
            unique_str = []
            for item in unique_combo:
                current_item = list(item)
                sep_str = ' %s ' % sep_item
                unique_str.append(sep_str.join(current_item))
            abstractions[abs_key] = unique_str
    # Save Abs data into CSV
    abs_loc = create_file('abstractions.csv', 'resources', 'console', subdomain)
    DataFrame.from_dict(data=abstractions, orient='index').transpose().to_csv(abs_loc, index=False)
    print("Field data saved in %s" % abs_loc)


def tag_extractions(tags):
    while True:
        tag_action = input(
            "Choose one of the actions to apply to field:" + "\n(1) Extract Key:Value \n(2) Extract by Separators" + \
            "\n(3) Extract by Custom Regex\n(next) To Access tag discovery" + \
            "\nChoice: ")
        if tag_action.lower() not in ['1', '2', '3', '4', 'next']:
            print("Invalid Input. Try Again.")
            continue

        # new_tags = deepcopy(tags)
        if tag_action == '1':
            while True:
                field_name = input("Choose the field name: ")
                if field_name not in tags:
                    print("Field name not found. Try again.")
                    continue
                break
            new_tags = extract_key_value(tags, field_name)
        elif tag_action == '2':
            while True:
                field_name = input("Choose the field name: ")
                if field_name not in tags:
                    print("Field name not found. Try again.")
                    continue
                break
            new_tags = extract_separators(tags, field_name)
        elif tag_action == '3':
            while True:
                field_name = input("Choose the field name: ")
                if field_name not in tags:
                    print("Field name not found. Try again.")
                    continue
                break
            regex = input("Enter your custom regex expression: ")
            extract_regex(regex, tags, field_name)
        elif tag_action == '4':
            # while True:
            #     modify_choice = input(
            #         "Do you want to modify:" + \
            #         "\n(1) Individual Field Values\n(2) All Field Values in a Field Key" + \
            #         "\nChoice: ")
            #     if modify_choice not in ["1", "2"]:
            #         print("Incorrect input. Try Again.")
            #         continue
            print("This isn't developed yet.")
        elif tag_action.lower() in ['next', 'nxt', 'nextt']:
            break
        print("Updated Tags..")

        tags = deepcopy(new_tags)

    return tags


def validating_token(token_type):
    while True:
        token = input("PagerDuty %s Key: " % token_type)

        # Validating Global Token
        if len(token) < 6:
            print("Length of the %s Token is too small. Enter a valid Token." % token_type)
            continue
        last_4_char = (len(token) - 4) * "*" + token[-4:]
        if not is_token_valid(token):
            print("Token '%s' you entered is invalid. Please retry." % last_4_char)
            continue
        else:
            break
    return token


if __name__ == "__main__":
    while True:
        disco_method = input(
            "Please choose one of the following discovery method by #." +
            "\n(1) Tag Discovery via Datadog API\n(2) Hostname/Tag Discovery via PagerDuty API" +
            "\n(3) Exit" +
            "\nChoose: "
        )
        if disco_method in ["1", "2", "3"]:
            disco_method = int(disco_method)
            break
        print("Incorrect input. Choose either '1' or '2'.\n\n")

    if disco_method == 1:
        run_datadog()
    if disco_method == 2:
        run_pagerduty()
