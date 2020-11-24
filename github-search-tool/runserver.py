from breqwatrapp import app
from config import Config

app.debug = True
app.secret_key = Config.SECRET_KEY

app.run()
