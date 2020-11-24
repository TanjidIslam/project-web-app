import os

from adaptapp import app

app.secret_key = b']\x1e\xc1C\xbbU"\xf1E\xebd\'\xe2\xd2:ft;/\xc4\x9c1\xfb\x8a'
app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.run(port=int(os.getenv('PORT', 8000)), debug=True, threaded=True)