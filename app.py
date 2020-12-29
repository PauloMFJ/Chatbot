from flask import Flask, render_template, redirect, url_for, json
from flask_socketio import SocketIO
import random
from datetime import datetime

# Setup socketio
app = Flask(__name__)
app.config['SECRET_KEY'] = '\xe3\xa3\xecK>\x82\xc1\xdfH=\xd0S\xb3\x9eX\x97\xfd\xeb\xefO\xdf\xda\x10\x96'
app.debug = True
socketio = SocketIO(app)

# Method to read data from JSON file
def load_json_file(filename):
    with app.open_resource('app/static/assets/configuration/' + filename + '.json') as f:
        return json.load(f)

class Message(object):
	queue = str()

	# Emit Ticket
	@staticmethod
	def emit_ticket(event_name, ticket_info):
		socketio.emit(event_name, ticket_info)

	# Emit message
	@staticmethod
	def emit_message(event_name, message):
		message = { 'message': Message.queue + message, 'time_sent': datetime.now().strftime("%H:%M") }
		Message.queue = str()
		socketio.emit(event_name, message)

	# Add message to queue
	@staticmethod
	def queue_message(event_name, message):
		Message.queue += message

	# Add feedback to queue
	@staticmethod
	def queue_feedback(event_name, feedback_name):
		feedbacks = load_json_file('feedback')[feedback_name]
		Message.queue += random.choice(feedbacks) + ' '

	# Emit feedback message
	@staticmethod
	def emit_feedback(event_name, feedback_name, string=str()):
		feedbacks = load_json_file('feedback')[feedback_name]
		feedback = Message.queue + random.choice(feedbacks)
		feedback = feedback.replace('%s', string)
		Message.queue = str()
		Message.emit_message(event_name, feedback)

# Get suffix type
def suffix(day):
    return 'th' if 11 <= day <=13 else { 1:'st', 2:'nd', 3:'rd'}.get(day % 10, 'th')

# Get and return custom datetime containing suffix
def custom_strftime(date, type_format):
    return date.strftime(type_format).replace('{S}', str(date.day) + suffix(date.day))

# Get and return string as date
def get_strptime(string):
	return datetime.strptime(string, '%d%m%y')

# Get and return formatted date string
def to_date(string):
    return str(custom_strftime(get_strptime(string), '{S} %B %Y'))

# Get and return date in passed in format
def custom_to_date(string, type_format):
    return str(datetime.strftime(get_strptime(string), type_format))

# Render Index
@app.route('/')
@app.route('/chatbot')
def index():
	return render_template('/index.html')

# Import modules
from nlpu import get_entities
from knowledge_base import process_entities

# Display welcome on connect
@socketio.on('connect')
def connect():
	Message.queue_feedback('display received message', 'welcome')
	process_entities({'reset': 'true'})

# Message handling
@socketio.on('message sent')
def handle_message(json, methods=['GET', 'POST']):
	# Display user message
	Message.emit_message('display sent message', json['message'])

	# Send feedback
	process_entities(get_entities(json))

if __name__ == '__main__':
    socketio.run(app)