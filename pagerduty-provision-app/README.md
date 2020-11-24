# ADAPT

ADAPT is a framework for PagerDuty consultants to run an algorithm on customer data to find suitable pattern that would provision services, route events, business services from Customer's monitoring tool to PagerDuty.

## Requirements

- Python 3.7.1+

## ADAPT Quick Start Guide

This guide will walk you through deploying ADAPT on localhost:

- [Installing Python 3.7.1](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#installing-python-371-on-mac)
- [Installing GitHub Desktop](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#downloading-and-installing-github-desktop)
- [Cloning Github Repository](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#Cloning-Github-Repository)
- [Updating Github Repository](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#Updating-Github-Repository)
- [Running on Local Server](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#Running-on-local-server)
- [Known Issues](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#known-issues)
- [TODO](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#todo)
- [Design Choices](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#Design-Choices)

Important Note: [To use customer's data and provision on your test account, follow this instruction.](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#running-test-provisions-using-customers-data)

## Features

- `/` : Choose to discover via PagerDuty event payload or Datadog tags for relevant hostname and product components
- `/authenticate` : [Access PagerDuty instance via PagerDuty API](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#access-pagerduty-instance)
  - Access Datadog and Dynatrace tags via PagerDuty API
  - Access hostnames from Nagios and associated forks via PagerDuty API
- `/authenticate`:[Access Datadog tags via Datadog API](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#access-datadog-instance)
- `/discovery/metadata`: Setup relevant metadata for provisioning phase
- `/discovery/services` and `/discovery/services/configure`: Discover events accross multiple services with the same payload pattern/fields in a consultant selected event window
- `/discovery/incidents`: Automatically discover appropriate fields to extract hostnames/tags for recognized integrations (Datadog, Dynatrace, Nagios, Check_MK) - all discovered fields/extraction will be listed on the navigation bar on the right-hand side of the page
- `/discovery/incidents`: For lesser recognized integrations or custom payload - [Discover hostnames/tags via events' custom fields discover](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#custom-fields-for-tagshostname-extractions)
- `/discovery/fields/multiple` and `/discovery/fields/single`: Analyze selected fields and extract for meaningful routing components (hostname, product, function name, region, etc.). **This will also be the first page if you choose Datadog discovery method**
  - Extract fields into key/value format if pattern matches
  - Extract fields if they are concatinated by a valid separators ('-', '_', ':', ',', etc.)
  - Extract fields using Regular Expression (Use [Regex101](https://regex101.com/)) to split components - tutorials/examples to be added
  - Assign custom and more meaningful names for selected components 
    - Can be done individually (`/discovery/fields/single`) or as a group (`/discovery/fields/multiple`)
- `/provision/combination/build`: Build multiple combinations of event routing components, while formatting for service abstraction names
- `/provision/combination/list`: List possible combinations of Service abstractions based on data from hostname/tags
- `/provision/preview`: Before provisioning, you can actually preview what data will be provisioned and how it would look like.
  - [Run a test/dummy provisioning by copying customer's tags/hostname data into your own test/dummy account](https://github.com/PagerDuty/es-adapt/tree/tislam-dev/adapt-core#running-test-provisions-using-customers-data)
- `/provision/preview`: Modify provisioning configurations
  - Choose whether or not to provision Business Services
  - Choose whether or not to provision Impact Metrics
  - Modify/Add Event Routing Path, if it is not being provisioned for recognized integration payloads (Datadog, Dynatrace, Nagios, Check_mk)
  - Choose Alert Creation Setting (Intelligent vs Time)
- `/provision/results`: Provision data based on your discovery, service abstract combinations and provisioning configuration
  - Services will be provisioned with best practice (Event Intelligence - can be changed)
  - Event Rules will be created to find patterns based on your combinations and route to created services
  - 1:1 Business services will be provisioned and associated with Services created during provisioning
  - Impact Metrics will be provisioned and associate with the created business services (Not functional) 
- `/provision/results`: Provides a report of what had been provisioned, and also provides the following option:
  - `Deprovision`:  Deprovision everything you've just provisioned. This can also be done later as long as you back up your `json` files from `resources/<customer_domain>/____.json` 
  - `Restart Session`: Wipe out all json file data and restart the session from scratch in the same account
  - `New Customer Session`:  Leave current session and relogin from the `/authentcate` page
- Download discovered and pre-provisioning data into spreadsheet/csv format
  - `/discovery/services`: Download all services in the working instance
  - `/discovery/incidents`: Download all events of chosen services
  - `/discovery/fields/multiple` and `/discovery/fields/single`: Download all chosen/selected fields for tag/hostname discovery
  - `/provision/combination/build`: Download all combination of service abstractions with field names
  - `/provision/combination/list`: Download all combination of service abstractions with customer data, to review with the customer
  - `/provision/preview`: Download preview of pre-provisioning data
  - `/provision/results`: Download result of provisioning (includes what was provisioned)

## Installing Python 3.7.1 on Mac (Method 1)

Currently, Mac OS comes with Python 2.7 built-in - which is good for starter but not for development as it has been retired. For this project to run, you'll need to install Python 3.7+.

#### Step 0: Check Python version

1. Open a terminal and type: `python3 --version`
2. If you get an error suggesting that you do not have Python 3, then go to Step (1). If you already have an older version of Python3, you have to update, follow Step (4)

#### Step 1: Install Homebrew (Part 1)

To get started, you first want to install Homebrew:

1. Open a browser and navigate to <http://brew.sh/>. After the page has finished loading, **select the Homebrew bootstrap code under “Install Homebrew”**. Then hit Cmd+C to copy it to the clipboard. Make sure you’ve captured the text of the complete command because otherwise the installation will fail.
2. Now you need to **open a Terminal.app window, paste the Homebrew bootstrap code, and then hit** Enter. This will begin the Homebrew installation.
3. If you’re doing this on a fresh install of macOS, you may get a pop up alert **asking you to install Apple’s “command line developer tools”**. You’ll need those to continue with the installation, so please **confirm the dialog box by clicking on “Install”**.

At this point, you’re likely waiting for the command line developer tools to finish installing, and that’s going to take a few minutes. Time to grab a coffee or tea!

#### Step 2: Install Homebrew (Part 2)

You can continue installing Homebrew and then Python after the command line developer tools installation is complete:

1. Confirm the “The software was installed” dialog from the developer tools installer.
2. Back in the terminal, hit Enter to continue with the Homebrew installation.
3. Homebrew asks you to enter your password so it can finalize the installation. **Enter your user account password and hit** Enter to continue.
4. Depending on your internet connection, Homebrew will take a few minutes to download its required files. Once the installation is complete, you’ll end up back at the command prompt in your terminal window.

Whew! Now that the Homebrew package manager is set up, let’s continue on with installing Python 3 on your system.

#### Step 3: Install Python

Once Homebrew has finished installing, **return to your terminal and run the following command**:

```shell
$ brew install python3
```

**Note:** When you copy this command, be sure you don’t include the `$` character at the beginning. That’s just an indicator that this is a console command.

This will download and install the latest version of Python. After the Homebrew `brew install` command finishes, Python 3 should be installed on your system.

You can make sure everything went correctly by testing if Python can be accessed from the terminal:

1. Open the terminal by launching **Terminal.app**.
2. Type `pip3` and hit Enter.
3. You should see the help text from Python’s “Pip” package manager. If you get an error message running `pip3`, go through the Python install steps again to make sure you have a working Python installation.

Assuming everything went well and you saw the output from Pip in your command prompt window…congratulations! You just installed Python on your system, and you’re all set to continue with the next section in this tutorial.

#### Step 4: Updating Python (If a version already exist)

1. Open the terminal by launching **Terminal.app**.
2. Type `brew update`
3. Then type `brew upgrade python3`

## Installing Python 3.7.1 on Mac using Pyenv (Method 2)

```bash
# Install pyenv
$ brew install pyenv

# Or Update if it already exists
$ brew upgrade pyenv #If pyenv is already installed

# Add Pyenv to your path
$ echo 'export PATH="$(pyenv root)/shims:$PATH"' >> ~/.zshrc
$ source ~/.zshrc

# Install the appropiate python version
$ pyenv install 3.7.1
```



## [Downloading and installing GitHub Desktop](https://help.github.com/en/desktop/getting-started-with-github-desktop/installing-github-desktop#downloading-and-installing-github-desktop)

You can install GitHub Desktop on macOS 10.10 or later .

1. Visit the [GitHub Desktop download page](https://desktop.github.com/).
2. Choose **Download for Mac**.
3. In your computer's **Downloads** folder, double-click the **GitHub Desktop** zip file.
4. After the file has been unzipped, double-click **GitHub Desktop**.

## Cloning Github Repository

The initial clone can be done via both terminal and Github Desktop application.

#### Terminal

Change directory to the root of the directory where you want to download the repository (in our example, it is `Documents/Github`):

```shell
$ cd Documents/Github
$ git clone --single-branch --branch tislam-dev https://github.com/PagerDuty/es-adapt.git
```

#### Github Desktop Application

```
~ Open Github Desktop
~ File >> Clone a Repository
~ Click on the URL tab
~ In the URL, copy and paste the following URL: https://github.com/PagerDuty/es-adapt.git 
~ Choose the local path where the Repository will be downloaded, then click on Clone
~ Once the repository is downloaded, click on Current Branch, then choose tislam-dev
```

## Updating Github Repository

Updating/pulling latest repository can be done via both terminal and Github Desktop Application. For convenience, we recommend using the Desktop Application as per the instructions below:

- Open the **Github Desktop Application**
- Check and ensure that the current branch is selected as **tislam-dev**
- Click on **Pull Origin**
- If you do not see **Pull Origin**, then click on **Fetch Origin**
- You should now have the latest version of the repository

## Running on Local Server Using venv (Ignore this step if you used pyenv)

Method 1: Run using Python3's default venv:

```shell
# Change current working directory to the root of adapt-core
$ cd es-adapt/adapt-core

# Create and activate virtual environment
$ python3 -m venv venv
$ source venv/bin/activate
```

## Install requirements

```bash
# Optional: Update pip to the latest version to avoid any errors
$ pip install --upgrade pip

# Install dependencies
$ pip3 install -r requirements.txt
```

To run on local server:

```shell
$ python3 localserver.py
```

Now, go to your preferred Internet Browser and enter one of the following URL:

- <http://localhost:8000/>
- <http://127.0.0.1:8000/>

To stop the application and deactivate virtual environment:

```shell
# Press control + C

# If you're running venv, Deactivate venv
(venv) $ deactivate
```



## KNOWN ISSUES

- Impact Metrics association doesn't work due to the API Update
- Events API has been inconsistent and responds with 400 for the same request it may respond with 200/301
  - Goal is to use the new CRUD method API endpoint which is still on early stage

## TODO

- Update Events API with the new API endpoint
- Provision via CSV file
- Provisioning Templates (JSON format)
- Mass update Service & Business Services
- Convert [File I/O](https://docs.python.org/3/tutorial/inputoutput.html) library to [logging](https://docs.python.org/3/library/logging.html) library for logs only

## Design Choices

Design choices are as important as application implementations. In this section, I will demonstrate on my choice of design and tools and point out how they connect. I used Model-View-Controller pattern, also known as the famous MVC pattern. I chose Python with Flask framework because it is light and gives me the freedom to use **routes, models, views & controllers**, the 4 major components of MVC pattern.

#### Routes

A user **requests** to view a page by entering a URL:

```
http://127.0.0.1:8000/discovery/services
```

The application matches the URL pattern with a predefined **route**:

```
http://127.0.0.1:8000/'discovery/services'
```

With each **route** is associated with a controller, more specifically a certain function within the controller, also known as the **controller action**:

```python
@app.route('/discovery/services', methods=['GET'])
def get_service_discovery():
    #doSomething
```

#### Models and Controllers

The **controller action** uses the models (services model for this case) to retrieve all of the necessary data from either user input or local variables, places the data in a data structure (dictionary/json in this case), and making api calls, passing along the data structure:

```python
@app.route('/provision/preview', methods=['POST'])
def post_provision_data():
  	service_name = request.form['name']
    ep_name = request.form['ep_id']
    alert_creation = request.form['alert_creation']
    alert_grouping = request.form['alert_grouping']
    
  	# All service entries in a dictionary
    new_service = provision_service(service_name, ep_name, alert_creation, alert_grouping)       
    ..
    ..
    return redirect(url_for('nexturl'))
    
def provision_service(service_abstraction, ep, alert_creation, alert_grouping):
    time_now = strftime('%Y-%m-%dT%H:%M:%S-00', gmtime(int(time())))
    new_service = Service(name=service_abstraction,
                          description="This service was created using the PagerDuty Expert Services ADAPT Solution. Provisioned at: " + time_now,
                          status="active",
                          escalation_policy=ep,
                          alert_creation=alert_creation,
                          alert_grouping=alert_grouping)
    return new_service


class Service(object):
    """ A Service Object """

    def __init__(self, name, description, status, escalation_policy, alert_creation, alert_grouping):
        """ A new Service with necessary fields """
        self.name = name
        self.description = description
        self.status = status
        self.escalation_policy = escalation_policy
        self.alert_creation = alert_creation
        self.alert_grouping = alert_grouping
```

#### Views

The **view**, the basic structure of data that was passed on by **controller action**, uses it to render the requested page, which is then displayed to the user in their browser.

```jinja2
<table id="serviceListExport" class="table table-bordered">
  <thead>
    <tr>
      {% for key in keys %}
        <th style="display: none">{{ key }}</th>
      {% endfor %}
    </tr>
  </thead>
  <tbody>
    {% for i in range(services|length) %}
      <tr>
        {% for key in keys %}
        	<td style="display: none">{{ services[i][key] }}</td>
        {% endfor %}
      </tr>
    {% endfor %}
  </tbody>
</table>
```

#### Project Context

```
adapt-core - contains models, views, templates, and front-end files (css, javascript, jqeuery, ajax)

models - This is where models are defined, contains service, business service, impact metrics and event rules structures, that can be used to create, update and get database entries for services, business services, impact metrics, and event rules

views - This is where routes are defined, contains all view functions with route() decorator

templates - This is where Jinja2 templates are defined, contains all pages files that routes communicate with

static - This is where all the front-end files are defined, contains all static that do not change and are used for user side


__init__.py - This file initializes the application and brings together all of the various components


config.py - This is where all the configuration variables are defined, contains variables like secret keys and database access


requirements.txt - This file lists all of the Python packages that the application depends on


run
	localserver.py - Run this application to deploy it on local server (http://127.0.0.1:8000)
```



## Functionalities

### Access PagerDuty Instance

PagerDuty instances can be accessed by authenticating [REST API Keys](https://support.pagerduty.com/docs/generating-api-keys#section-rest-api-keys) and [User API Keys](https://support.pagerduty.com/docs/generating-api-keys#section-generating-a-personal-rest-api-key). Currently, ADAPT framework can automatically detect tags from **Datadog** and **Dynatrace**, and hostnames from **Nagios** and its forks. However, you can also, manually select fields to analyze. 

### Access Datadog Instance

Datadog instances can be accessed by authenticating both of PagerDuty's [REST API Keys](https://support.pagerduty.com/docs/generating-api-keys#section-rest-api-keys) and [User API Keys](https://support.pagerduty.com/docs/generating-api-keys#section-generating-a-personal-rest-api-key), and also both of Datadog's [API Keys](https://docs.datadoghq.com/account_management/api-app-keys/#api-keys) and [App Keys](https://docs.datadoghq.com/account_management/api-app-keys/#application-keys). This will allow ADAPT to automatically obtain data from Datadog's [tags](https://docs.datadoghq.com/tagging/) field.

### Custom Fields for Tags/Hostname Extractions

If you are analyzing a service that do not have payloads based on our recognized integrations such as **Datadog**, **Dynatrace**, **Nagios**/its forks (such as: **Check_mk**), then you can still analyze fields to extract combinations for Services and event routing. 

- Authenticate using [REST API Keys](https://support.pagerduty.com/docs/generating-api-keys#section-rest-api-keys) and [User API Keys](https://support.pagerduty.com/docs/generating-api-keys#section-generating-a-personal-rest-api-key)
- Page `/discovery/services`: Select your desired services with equivalent/similar payloads, then run an event discovery within an appropiate window
- Page `/discovery/incidents`: Analyze individual event, expand details/first time log entry. Check fields that you want to analyze for tags/hostnames, then from Actions bar on the right choose *Add Selected Fields for Tag Discovery* and click on *Update Tags*
- Page `/provision/preview`: It is extremely important to choose the events routing path from the payload and it can be selected when you are previewing possible abstractions for provisioning. At this stage, on the right navigation bar *Provision Preview*, select `Modify Provisioning Configuration` from the dropdown. Prior to this step, request customer to send a test incident to their routing key so you can capture the required routing fields. Once you captured the routing key, please enter that on the **Event Routing Path:** field and save configuration

### Running Test Provisions using Customer's data

Once you have previewed data that you want to provision, you can log out of customer's account and run a test run by provisioning customer's data (services/event rules/biz services/impact metrics) into a dummy account (or your pdt-test account) instead of customer's account, do the following:

- Go to the root of the adapt-core project folder

- Access the resources folder, then customer's folder (resources >> customer_subdomain_folder)

- Copy all json file except for `session.json`: 

  - abstractions.json
  - api_logs.json
  - changes.json
  - combos.json
  - incidents.json (may not exist if customer's instance is based on Datadog)
  - separators.json
  - service.json
  - service_abstraction.json
  - str_abstractions.json
  - tag_combo.json
  - tags.json
  - template.json
  - types.json

- Create another folder (or access existing one if you've already logged in once) in the resources directory and name it the subdomain of your dummy or test account (i.e. pdt-tislam-test)

- Paste those 11-12 json files in that test/dummy pd account folder

- Now authenticate using your test/dummy account's api keys and access the Services page (`/discovery/services`)

- Page `/discovery/services`: 

  - `tags/hostname abstractions`: You can access tags/hostname extractions from customer's account directly. You should see: `Customized Tags Found: Previous session was found. Click here to access tags directly.` Simply click on that link to access tags/hostname abstractions.. If you can also click on the tab on navigation bar called `Abstraction Discovery` to access these tags/hostname abstractions.
  - `Provision test`: You can navigate to the preview of provision data. You should see: `PREVIOUS PREVIEWED PROVISIONING DATA WAS FOUND ON THIS INSTANCE. Click here to view previewed data.` Simply click on that link to access the provision preview data, then provision to your dummy account for test purpose.
  - `Redo Combo`: This step must be done via `tags/hostname abstractions`
  