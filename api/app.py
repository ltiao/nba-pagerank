import itertools
import logging

import connexion


app = connexion.App(__name__)
app.add_api('swagger.yaml', base_path='/api')

# set the WSGI application callable to allow using uWSGI:
# uwsgi --http :8080 -w app
# application = app.app


if __name__ == '__main__':
    # Start server
    app.run(port=8080, debug=True)
