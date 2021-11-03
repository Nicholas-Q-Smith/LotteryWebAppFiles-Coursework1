# IMPORTS
import logging
import socket
from functools import wraps
from flask import Flask, render_template, request
from flask_login import LoginManager, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman

# LOGGING

class SecurityFilter(logging.Filter):
    def filter(self, record):
        return "SECURITY" in record.getMessage()


fh = logging.FileHandler('lottery.log', 'w')
fh.setLevel(logging.WARNING)
fh.addFilter(SecurityFilter())
formatter = logging.Formatter('%(asctime)s : %(message)s', '%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

logger = logging.getLogger('')
logger.propagate = False
logger.addHandler(fh)

# CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lottery.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'LongAndRandomSecretKey'
app.config['RECAPTCHA_PUBLIC_KEY'] = "6LfFdRMcAAAAAEeOwLocqoG8LhRNZhE0TYF8MdMG"
app.config['RECAPTCHA_PRIVATE_KEY'] = "6LfFdRMcAAAAAILSgmbrJcTLnkDV5fG-xwPzyoR4"

# initialise database
db = SQLAlchemy(app)
# Security Headers

csp = {'default-src': ['\'self\'', 'https://cdnjs.cloudflare.com/ajax/libs/bulma/0.7.2/css/bulma.min.css'],
       'script-src': ['\'self\'', '\'unsafe-inline\'', 'https://www.google.com/recaptcha/',
                       'https://www.gstatic.com/recaptcha/'],
        'frame-src': ['https://www.google.com/recaptcha/',
                      'https://www.recaptcha.google.com.com/recaptcha/']}

talisman = Talisman(app, content_security_policy=csp)


# FUNCTIONS
def requires_roles(*roles):
    def wrapper(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if current_user.role not in roles:
                logging.warning('SECURITY - Unauthorised access attempt [%s, %s, %s, %s]',
                                current_user.id,
                                current_user.email,
                                current_user.role,
                                request.remote_addr)
                # Redirect the user to an unauthorised notice!
                return render_template('403.html')
            return f(*args, **kwargs)
        return wrapped
    return wrapper


# HOME PAGE VIEW
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == "__main__":
    logging.warning('SECURITY - Lottery Web App Started')
    my_host = "127.0.0.1"
    free_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    free_socket.bind((my_host, 0))
    free_socket.listen(5)
    free_port = free_socket.getsockname()[1]
    free_socket.close()

    # BLUEPRINTS
    # import blueprints
    from users.views import users_blueprint
    from admin.views import admin_blueprint
    from lottery.views import lottery_blueprint

    login_manager = LoginManager()
    login_manager.login_view = 'users.login'
    login_manager.init_app(app)

    from models import User


    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    # register blueprints with app
    app.register_blueprint(users_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(lottery_blueprint)

    app.run(host=my_host, port=free_port, debug=True)