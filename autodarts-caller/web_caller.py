from flask import Flask, render_template, send_from_directory
from urllib.parse import unquote
import os
import threading

from caller_configuration import CallerConfiguration
from globals import CALLER_LANGUAGES, CALLER_GENDERS
from defaults import DEFAULT_HOST_IP


class WebCaller:
    app: Flask = Flask(__name__)
    config: CallerConfiguration

    def __init__(self, name, host, port, ssl_context, config: CallerConfiguration):
        self.config = config
        self.app = Flask(name)
        self.host = host
        self.port = port
        self.ssl_context = ssl_context

    def start_flask_app(self):
        if self.ssl_context is None:
            self.app.run(host=self.host, port=self.port, debug=False)
        else:
            self.app.run(ssl_context=self.ssl_context, host=self.host, port=self.port, debug=False)
        self.flask_app_thread = threading.Thread(target=self.start_flask_app, args=(self.host, self.port, self.ssl_context))
        self.flask_app_thread.start()

    def start(self):
        @self.app.route('/')
        def index():
            return render_template('index.html', host=DEFAULT_HOST_IP, 
                                                    app_version=self.config.VERSION, 
                                                    db_name=self.config.WEB_DB_NAME, 
                                                    ws_port=self.config.HOST_PORT, 
                                                    state=self.config.WEB, 
                                                    id=currentMatch,
                                                    me=self.config.AUTODART_USER_BOARD_ID,
                                                    meHost=currentMatchHost,
                                                    players=currentMatchPlayers,
                                                    languages=CALLER_LANGUAGES, 
                                                    genders=CALLER_GENDERS,
                                                    language=self.config.RANDOM_CALLER_LANGUAGE,
                                                    gender=self.config.RANDOM_CALLER_GENDER
                                                    )

        @self.app.route('/sounds/<path:file_id>', methods=['GET'])
        def sound(file_id):
            file_id = unquote(file_id)
            file_path = file_id
            if os.name == 'posix':  # Unix/Linux/MacOS
                directory = '/' + os.path.dirname(file_path)
            else:  # Windows
                directory = os.path.dirname(file_path)
            file_name = os.path.basename(file_path)
            return send_from_directory(directory, file_name)

        @self.app.route('/scoreboard')
        def scoreboard():
            return render_template('scoreboard.html', host=DEFAULT_HOST_IP, ws_port=self.config.HOST_PORT, state=self.config.WEB_CALLER_SCOREBOARD)
        self.start_flask_app(self.host, self.port, self.ssl_context)