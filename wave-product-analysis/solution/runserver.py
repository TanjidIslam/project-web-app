import os
from config import Config
from solution import app

# Running the application on local server with port 8000
app.run(port=int(os.getenv('PORT', 8000)), debug=Config.DEBUG)
