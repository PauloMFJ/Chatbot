import requests, json
from bs4 import BeautifulSoup
from app import custom_to_date

class Ticket(object):
    url = str()

    @staticmethod
    def get_ticket_single(fromLocation, toLocation, departDate, departTime):
        parsed_html = Ticket.request_page_single(fromLocation, toLocation, departDate, departTime)
        return Ticket.get_cheapest_ticket(parsed_html, False, departDate, None)

    @staticmethod
    def get_ticket_return(fromLocation, toLocation, departDate, departTime, returnDate, returnTime):
        parsed_html = Ticket.request_page_return(fromLocation, toLocation, departDate, departTime, returnDate, returnTime)
        return Ticket.get_cheapest_ticket(parsed_html, True, departDate, returnDate)

    @staticmethod
    def request_page_single(fromLocation, toLocation, departDate, departTime):
        url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + fromLocation + '/' + toLocation
            + '/' + departDate + '/' + departTime + '/dep')
        return Ticket.get_page_contents(url)

    @staticmethod
    def request_page_return(fromLocation, toLocation, departDate, departTime, returnDate, returnTime):
        url = ('http://ojp.nationalrail.co.uk/service/timesandfares/' + fromLocation + '/' + toLocation
            + '/' + departDate + '/' + departTime + '/dep/' + returnDate + '/' + returnTime + '/dep')
        return Ticket.get_page_contents(url)

    @staticmethod
    def get_page_contents(url):
        Ticket.url = url
        r = requests.get(url)
        return BeautifulSoup(r.text, 'html.parser')

    @staticmethod
    def get_cheapest_ticket(page_contents, isReturn, departDate, returnDate):
        try:
            info = json.loads(page_contents.find('script', {'type':'application/json'}).text)

            ticket = {}
            ticket['url'] = Ticket.url
            ticket['isReturn'] = isReturn
            ticket['departDate'] = custom_to_date(departDate, '%d-%b-%Y')
            ticket['departureStationName'] = str(info['jsonJourneyBreakdown']['departureStationName'])
            ticket['arrivalStationName'] = str(info['jsonJourneyBreakdown']['arrivalStationName'])
            ticket['departureTime'] = str(info['jsonJourneyBreakdown']['departureTime'])
            ticket['arrivalTime'] = str(info['jsonJourneyBreakdown']['arrivalTime'])
            durationHours = str(info['jsonJourneyBreakdown']['durationHours'])
            durationMinutes = str(info['jsonJourneyBreakdown']['durationMinutes'])
            ticket['duration'] = (durationHours + 'h ' + durationMinutes + 'm')
            ticket['changes'] = str(info['jsonJourneyBreakdown']['changes'])

            if isReturn:
                ticket['returnDate'] = custom_to_date(returnDate, '%d-%b-%Y')
                ticket['fareProvider'] = info['returnJsonFareBreakdowns'][0]['fareProvider']
                ticket['returnTicketType'] = info['returnJsonFareBreakdowns'][0]['ticketType']
                ticket['ticketPrice'] = info['returnJsonFareBreakdowns'][0]['ticketPrice']
            else:
                ticket['fareProvider'] = info['singleJsonFareBreakdowns'][0]['fareProvider']
                ticket['ticketPrice'] = info['singleJsonFareBreakdowns'][0]['ticketPrice']

            return ticket
        except:
            return False