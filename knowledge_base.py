from experta import *
from experta.watchers import RULES, AGENDA
import dateutil.parser
from datetime import datetime

from web_scrape import Ticket

class Booking(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        if 'reset' in self.dictionary:
            if self.dictionary.get('reset') == 'true':
                self.knowledge = {}
                self.dictionary['service'] = 'chat'

        # Get Service
        service = self.dictionary.get('service')
        if 'service' in self.knowledge:
            if service != 'chat':
                name = self.knowledge.get('name')
                self.knowledge = {}
                self.knowledge['name'] = name
                self.knowledge['service'] = service
        else:
            self.knowledge['service'] = service
        yield Fact(service = self.knowledge.get('service'))

        # Set knowledge
        if not 'question' in self.knowledge:
            self.knowledge['question'] = str()

        if 'name' in self.knowledge:
            yield Fact(name = self.knowledge.get('name'))
        if 'isReturn' in self.knowledge:
            yield Fact(isReturn = self.knowledge.get('isReturn'))
        if 'fromLocation' in self.knowledge:
            yield Fact(fromLocation = self.knowledge.get('fromLocation'))
        if 'toLocation' in self.knowledge:
            yield Fact(toLocation = self.knowledge.get('toLocation'))

        if 'departDate' in self.knowledge:
            yield Fact(departDate = self.knowledge.get('departDate'))
        if 'departTime' in self.knowledge:
            yield Fact(departTime = self.knowledge.get('departTime'))
        if 'returnDate' in self.knowledge:
            yield Fact(returnDate = self.knowledge.get('returnDate'))
        if 'returnTime' in self.knowledge:
            yield Fact(returnTime = self.knowledge.get('returnTime'))

        if 'givenTicket' in self.knowledge:
            yield Fact(givenTicket = self.knowledge.get('givenTicket'))
        if 'whatsNext' in self.knowledge:
            yield Fact(whatsNext = self.knowledge.get('whatsNext'))

        if 'predictFromLocation' in self.knowledge:
            yield Fact(predictFromLocation = self.knowledge.get('predictFromLocation'))
        if 'predictToLocation' in self.knowledge:
            yield Fact(predictToLocation = self.knowledge.get('predictToLocation'))
        if 'predictDepartTime' in self.knowledge:
            yield Fact(predictDepartTime = self.knowledge.get('predictDepartTime'))
        if 'predictReturnTime' in self.knowledge:
            yield Fact(predictReturnTime = self.knowledge.get('predictReturnTime'))
        if 'predictDelay' in self.knowledge:
            yield Fact(predictDelay = self.knowledge.get('predictDelay'))
        if 'informationGiven' in self.knowledge:
            yield Fact(informationGiven = self.knowledge.get('informationGiven'))

    # Greeting
    @Rule(salience = 100)
    def greeting(self):
        if 'greeting' in self.dictionary:
            Message.queue_feedback('display received message', 'greeting')

    # Ask Name
    @Rule(Fact(service = 'chat'),
        NOT(Fact(name = W())),
        salience = 99)
    def ask_name(self):
        if 'name' in self.dictionary:
            name = self.dictionary.get('name')
            self.declare(Fact(name = name))
            self.knowledge['name'] = name
        else:
            if self.knowledge['question'] == 'ask_name':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_name'
            Message.emit_feedback('display received message', 'ask_name')

    # Ask Service
    @Rule(Fact(service = 'chat'),
        Fact(name = MATCH.name),
        salience = 98)
    def ask_if_booking(self, name):
        if self.knowledge['question'] == 'ask_if_booking':
            Message.emit_feedback('display received message', 'unknown_message')
        else:
            self.knowledge['question'] = 'ask_if_booking'
        Message.emit_feedback('display received message',  'ask_make_booking', name)

    # Ask Location
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(fromLocation = W())),
        NOT(Fact(toLocation = W())),
        salience = 97)
    def ask_location(self):
        error = False
        if 'location' in self.dictionary and len(self.dictionary.get('location')) > 1:
            location = self.dictionary.get('location')
            self.declare(Fact(fromLocation = location[0]))
            self.knowledge['fromLocation'] = location[0]
            self.declare(Fact(toLocation = location[1]))
            self.knowledge['toLocation'] = location[1]
        else:
            if self.knowledge['question'] == 'ask_location':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_location'
            Message.emit_feedback('display received message', 'ask_location')
            self.declare(Fact(isQuestion = True))

    # Ask Depart Date
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(departDate = W())),
        salience = 96)
    def ask_depart_date(self):
        departDate = 'false'
        error = False
        if 'dates' in self.dictionary:
            departDate = self.dictionary.get('dates')[0]
            if dateutil.parser.parse(departDate) < datetime.now():
                Message.emit_feedback('display received message', 'past_date')
                error = True
            else:
                self.declare(Fact(departDate = departDate))
                self.knowledge['departDate'] = departDate

        if self.knowledge['question'] == 'ask_depart_date' and departDate == 'false' and not error:
            Message.emit_feedback('display received message', 'wrong_date')
        else:
            self.knowledge['question'] = 'ask_depart_date'

        if departDate == 'false' or error:
            Message.emit_feedback('display received message', 'ask_depart_date')
            self.declare(Fact(isQuestion = True))

    # Ask Depart Time
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(departTime = W())),
        salience = 95)
    def ask_depart_time(self):
        if 'times' in self.dictionary:
            departTime = self.dictionary.get('times')
            self.declare(Fact(departTime = departTime[0]))
            self.knowledge['departTime'] = departTime[0]
            del self.dictionary['times']
        else:
            if self.knowledge['question'] == 'ask_depart_time':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_depart_time'
            Message.emit_feedback('display received message', 'ask_depart_time')
            self.declare(Fact(isQuestion = True))

    # Ask If Return
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(isReturn = W())),
        salience = 94)
    def ask_is_return(self):
        if 'return' in self.dictionary:
            self.declare(Fact(isReturn = 'true'))
            self.knowledge['isReturn'] = 'true'
        elif 'answer' in self.dictionary:
            answer = self.dictionary.get('answer')
            self.declare(Fact(isReturn = answer))
            self.knowledge['isReturn'] = answer
            del self.dictionary['answer']
        else:
            if self.knowledge['question'] == 'ask_is_return':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_is_return'
            Message.emit_feedback('display received message', 'ask_is_return')
            self.declare(Fact(isQuestion = True))

    # Ask Return Date
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        Fact(isReturn = 'true'),
        NOT(Fact(returnDate = W())),
        salience = 93)
    def ask_return_date(self):
        returnDate = 'false'
        error = False
        if 'dates' in self.dictionary:
            returnDate = self.dictionary.get('dates')
            returnDate = returnDate[1] if len(returnDate) > 1 else returnDate[0]
            if dateutil.parser.parse(returnDate) < dateutil.parser.parse(self.knowledge.get('departDate')):
                Message.emit_feedback('display received message', 'past_depart_date')
                error = True
            else:
                self.declare(Fact(returnDate = returnDate))
                self.knowledge['returnDate'] = returnDate

        if self.knowledge['question'] == 'ask_return_date' and returnDate == 'false' and not error:
            Message.emit_feedback('display received message', 'wrong_date')
        else:
            self.knowledge['question'] = 'ask_return_date'

        if returnDate == 'false' or error:
            Message.emit_feedback('display received message', 'ask_return_date')
            self.declare(Fact(isQuestion = True))

    # Ask Return Time
    @Rule(Fact(service = 'book'),
        NOT(Fact(isQuestion = W())),
        Fact(isReturn = 'true'),
        NOT(Fact(returnTime = W())),
        salience = 92)
    def ask_return_time(self):
        if 'times' in self.dictionary:
            returnTime = self.dictionary.get('times')
            returnTime = returnTime[1] if len(returnTime) > 1 else returnTime[0]
            self.declare(Fact(returnTime = returnTime))
            self.knowledge['returnTime'] = returnTime
        else:
            if self.knowledge['question'] == 'ask_return_time':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_return_time'
            Message.emit_feedback('display received message', 'ask_return_time')
            self.declare(Fact(isQuestion = True))

    # Show Single Ticket
    @Rule(Fact(service = 'book'),
        NOT(Fact(givenTicket = W())),
        Fact(isReturn = 'false'),
        Fact(fromLocation = MATCH.fromLocation),
        Fact(toLocation = MATCH.toLocation),
        Fact(departDate = MATCH.departDate),
        Fact(departTime = MATCH.departTime),
        salience = 91)
    def show_single_ticket(self, fromLocation, toLocation, departDate, departTime):
        if not 'givenTicket' in self.knowledge:
            ticket = Ticket.get_ticket_single(fromLocation, toLocation, departDate, departTime)
            if not ticket:
                Message.emit_feedback('display received message', 'ticket_error')
                Message.emit_feedback('display received message', 'make_another_booking')
                self.declare(Fact(givenTicket = False))
                self.knowledge['givenTicket'] = False
            else:
                Message.emit_feedback('display received message', 'ticket_found_single')
                Message.emit_ticket('display ticket', ticket)
                self.knowledge['url'] = ticket.get('url')
                self.declare(Fact(givenTicket = True))
                self.knowledge['givenTicket'] = True

    # Show Return ticket
    @Rule(Fact(service = 'book'),
        NOT(Fact(givenTicket = W())),
        Fact(isReturn = 'true'),
        Fact(fromLocation = MATCH.fromLocation),
        Fact(toLocation = MATCH.toLocation),
        Fact(departDate = MATCH.departDate),
        Fact(departTime = MATCH.departTime),
        Fact(returnDate = MATCH.returnDate),
        Fact(returnTime = MATCH.returnTime),
        salience = 90)
    def show_return_ticket(self, fromLocation, toLocation, departDate, departTime, returnDate, returnTime):
        if not 'givenTicket' in self.knowledge:
            ticket = Ticket.get_ticket_return(fromLocation, toLocation, departDate, departTime, returnDate, returnTime)
            if not ticket:
                Message.emit_feedback('display received message', 'ticket_error')
                Message.emit_feedback('display received message', 'make_another_booking')
                self.declare(Fact(givenTicket = False))
                self.knowledge['givenTicket'] = False
            else:
                Message.emit_feedback('display received message', 'ticket_found_return')
                Message.emit_ticket('display ticket', ticket)
                self.knowledge['url'] = ticket.get('url')
                self.declare(Fact(givenTicket = True))
                self.knowledge['givenTicket'] = True

    # Ask Confirm Booking
    @Rule(Fact(service = 'book'),
        Fact(givenTicket = True),
        salience = 89)
    def confirm_booking(self):
        if 'answer' in self.dictionary:
            if self.dictionary.get('answer') == 'true':
                Message.queue_feedback('display received message', 'url')
                Message.emit_message('display received message', '<a href="' + self.knowledge.get('url') + '">' + self.knowledge.get('url') + '</a>')
            Message.queue_feedback('display received message', 'thank_you')
            self.knowledge['givenTicket'] = False
            self.declare(Fact(whatsNext = True))
            self.knowledge['whatsNext'] = True
            del self.dictionary['answer']
        else:
            if self.knowledge['question'] == 'confirm_booking':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'confirm_booking'
            Message.emit_feedback('display received message', 'confirm_booking')

    # Ask Predict Location
    @Rule(Fact(service = 'predict'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(predictFromLocation = W())),
        NOT(Fact(predictToLocation = W())),
        salience = 88)
    def ask_predict_location(self):
        if 'location' in self.dictionary and len(self.dictionary.get('location')) > 1:
            location = self.dictionary.get('location')
            self.declare(Fact(predictFromLocation = location[0]))
            self.knowledge['predictFromLocation'] = location[0]
            self.declare(Fact(predictToLocation = location[1]))
            self.knowledge['predictToLocation'] = location[1]
            del self.dictionary['location']
        else:
            if self.knowledge['question'] == 'ask_predict_location':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_predict_location'
            Message.emit_feedback('display received message', 'ask_predict_location')
            self.declare(Fact(isQuestion = True))

    # Ask Predict Depart Time
    @Rule(Fact(service = 'predict'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(predictDepartTime = W())),
        salience = 87)
    def ask_predict_depart_time(self):
        if 'times' in self.dictionary:
            predictDepartTime = self.dictionary.get('times')
            self.declare(Fact(predictDepartTime = predictDepartTime[0]))
            self.knowledge['predictDepartTime'] = predictDepartTime[0]
            del self.dictionary['times']
        else:
            if self.knowledge['question'] == 'ask_predict_depart_time':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_predict_depart_time'
            Message.emit_feedback('display received message', 'ask_predict_depart_time')
            self.declare(Fact(isQuestion = True))

    # Ask Predict Return Time
    @Rule(Fact(service = 'predict'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(predictReturnTime = W())),
        salience = 86)
    def ask_predict_return_time(self):
        if 'times' in self.dictionary:
            predictReturnTime = self.dictionary.get('times')
            predictReturnTime = predictReturnTime[1] if len(predictReturnTime) > 1 else predictReturnTime[0]
            self.declare(Fact(predictReturnTime = predictReturnTime))
            self.knowledge['predictReturnTime'] = predictReturnTime
            del self.dictionary['times']
        else:
            if self.knowledge['question'] == 'ask_predict_return_time':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_predict_return_time'
            Message.emit_feedback('display received message', 'ask_predict_return_time')
            self.declare(Fact(isQuestion = True))

    # Ask Delay
    @Rule(Fact(service = 'predict'),
        NOT(Fact(isQuestion = W())),
        NOT(Fact(predictDelay = W())),
        salience = 85)
    def ask_predict_delay(self):
        if 'minutes' in self.dictionary:
            minutes = self.dictionary.get('minutes')[0]
            self.declare(Fact(predictDelay = minutes))
            self.knowledge['predictDelay'] = minutes
            self.declare(Fact(informationGiven = False))
            self.knowledge['informationGiven'] = False
            del self.dictionary['minutes']
        else:
            if self.knowledge['question'] == 'ask_predict_delay':
                Message.emit_feedback('display received message', 'unknown_message')
            else:
                self.knowledge['question'] = 'ask_predict_delay'
            Message.emit_feedback('display received message', 'ask_predict_delay')
            self.declare(Fact(isQuestion = True))

    @Rule(Fact(service = 'predict'),
        Fact(informationGiven = False),
        salience = 84)
    def predict_delay(self):
        # To Do: Add Train Delay Prediction Component
        Message.emit_feedback('display received message', 'prediction_error')
        self.knowledge['informationGiven'] = True
        self.declare(Fact(whatsNext = True))
        self.knowledge['whatsNext'] = True

    # Ask What's Next
    @Rule(Fact(whatsNext = True),
        salience = 83)
    def whats_next(self):
        if self.knowledge['question'] == 'whats_next':
            Message.emit_feedback('display received message', 'unknown_message')
        else:
            self.knowledge['question'] = 'whats_next'
        Message.emit_feedback('display received message', 'whats_next')


# Initialize new booking
engine = Booking()
engine.knowledge = {}

# Set dictionary and run knowledge engine
def process_entities(entities):
    engine.dictionary = entities
    engine.reset()
    engine.run()

# Import Message
from app import Message, to_date