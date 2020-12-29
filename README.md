# Chatbot

Python-based intelligent chatbot system to find and book train tickets.

## Libraries Used

- [Flask](http://flask.pocoo.org/) and [Socket.IO](https://socket.io/) - Using Python for UI.
- [spaCy](https://spacy.io/) - Natural Language Processing and Understanding (NLPU) component.
- [PyKnow](https://pyknow.readthedocs.io/en/stable/) - Knowledge-Base (KB) and Reasoning Engine (RE) component.
- [Beautiful Soup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) - Web scraping component for retrieving ticket information.

Additionally used HTML, CSS, JavaScript, [JQuery](https://jquery.com/) and JSON.

## Build Setup

``` bash
# Create virtualenv
virtualenv venv
./venv/scripts/activate

# Install dependencies
pip install -r requirements.txt

# Run app
python app.py

# Install new dependency
python -m pip install ...
python -m pip freeze > requirements.txt

# See whats installed
pip list

```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for further details.

Contents of this site by [Paulo Jorge](http://www.bypaulo.design/). All rights reserved.
