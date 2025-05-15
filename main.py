from modules import create_app
from werkzeug.exceptions import HTTPException
#from exceptions.db import DuplicateRecordException
import re

from flask import session, request, redirect, url_for, abort, make_response, render_template

app = create_app('./config_dev.toml')


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
