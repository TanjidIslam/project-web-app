# mobile-challenge
This application retrieves the list of products for a specific business ID 
  > Then lists all the products to the user with the product name and price formatted in a dollar amount (Assuming that they're dollar, no cents)

## Project Description
In this project, I'm going to be creating a simple web application that shows a Wave user the products that they can charge for on their invoices. 

I'll be using the public Wave API in this challenge.The API documentation [here](http://docs.waveapps.io/). I will specifically be interested in [the products endpoint](http://docs.waveapps.io/endpoints/products.html#get--businesses-business_id-products-), and [using an access token with the API](http://docs.waveapps.io/oauth/index.html#use-the-access-token-to-access-the-api). 

### What your application must do:

1. App must retrieve the list of products for the specific business ID sent to you by your Wave contact
1. The list of products should be fetched and shown to the user in a list view when the app is launched.
1. Each item in the list view should show the product name and price (formatted as a dollar amount.)


### Why am I proud of this implementation?

I am proud of my implementation because:
- This implementation is built based on MVC design pattern. 
  - Controllers: @app.route is associated with Controller function, specifically a function, known as a controller action. When the user enters the URL, the application looks for a matching route and calls that route's associated controller action. 
  - Models: Within the controller action, the Model is used to collect data from the Product Endpoint request as a data structure (Json->List of Dictionaries, in this case) and passed to view in an appropriate structure (object in this case).
  - Views: View accesses the data and uses the information to render HTML content of the page that user sees at the end using Jinja2.
- I saved unnecessary hassle of converting JSON into a different data structure then populating that into an instance of product object by directly converting JSON->dictionary elements into an Object
- My implemented solution is organized and easy to understand
- This implementation can be viewed on the laptop or phone

PS: If you want me to do something more than just this, please let me know. 


#### Requirements
- Install Python from: https://www.python.org/downloads/
- Install Flask from shell/command prompt: pip install flask
- Install requests from shell/command prompt: pip install requests

#### Running The App:
- Download this repository
- Go to solution folder
  - Using shell/command prompt > python runserver.py
  - Using IDE: Open runserver.py and run it
- You should see the following > * Running on http://127.0.0.1:8000/ (Press CTRL+C to quit)

#### Viewing The App:
- Go on your Internet Browser (Google Chrome is recommended)
- Type: http://127.0.0.1:8000/ and hit enter
- This should give you a Desktop View
- Now for the Mobile View:
  - Press F12
  - For Chrome: Click on Toggle Device Mode or Press Ctrl+Shift+M
    - Select any device from the option from Responsive dropdown
  - For Firefox: Click on Responsive Mode
    - Select a resolution below 1020 for ipad and between 320 to 760 for mobile devices
