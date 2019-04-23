# also look into this progress bar library
# https://blog.sicara.com/perfect-python-command-line-interfaces-7d5d4efad6a2
# https://pypi.org/project/tqdm/
from tqdm import tqdm
from progress.bar import Bar
from datetime import datetime
import sqlite3
import time
# python -m pip install selenium
from selenium import webdriver
import queue

# referenced below for History SQLite schema
# https://digital-forensics.sans.org/blog/2010/01/21/google-chrome-forensics/

# maybe import chromedriver.exe into C:\Program Files\Python3.6.1\Scripts
# browser = webdriver.Chrome()
# browser.close()

# LINK
# TYPED
# AUTO_BOOKMARK
# MANUAL_SUBFRAME
# GENERATED
# START_PAGE
# FORM_SUBMIT
# KEYWORD_GENERATED

# AUTO_SUBFRAME
# RELOAD
# KEYWORD_GENERATED

# https://kb.digital-detective.net/display/BF/Page+Transitions
page_transitions = [("LINK", "User got to this page by clicking a link on another page."),
                     ("TYPED", "User got to this page by typing the URL in the URL bar. Should not be used for cases where the user selected a choice that didn't look at all like a URL; see GENERATED. Also used for other \"explicit\" navigation actions."),
                     ("AUTO_BOOKMARK", "User got to this page through a suggestion in the UI, for example, through the Destinations page."),
                     ("AUTO_SUBFRAME", "This is a subframe navigation.  This is any content that is automatically loaded in a non-toplevel frame.  For example, if a page consists of several frames containing ads, those ad URLs will have this transition type.  The user may not even realise the content in these pages is a separate frame, so may not care about the URL (see MANUAL)"),
                     ("MANUAL_SUBFRAME", "For subframe navigations that are explicitly requested by the user and generate new navigation entries in the back/forward list.  These are probably more important than frames that were automatically loaded in the background because the user probably cares about the fact that this link was loaded."),
                     ("GENERATED", "User got to this page by typing in the URL bar and selecting an entry that did not look like a URL.  For example, a match might have the URL of a Google search result page, but appear like \"Search Google for ...\".  These are not quite the same as TYPED navigations because the user didn't type or see the destination URL. See also KEYWORD."),
                     ("START_PAGE", "The page was specified in the command line or is the start page."),
                     ("FORM_SUBMIT", "The user filled out values in a form and submitted it.  NOTE that in some situations submitting a form does not result in this transition type.  This can happen if the form uses script to submit the contents."),
                     ("RELOAD", "The user \"reloaded\" the page, either by hitting the reload button or by hitting enter in the address bar.  NOTE that this is distinct from the concept of whether a particular load uses \"reload semantics\" (i.e. bypasses cached data). SessionRestore and undo tab close also use this transition type."),
                     ("KEYWORD", "The url was generated from a replaceable keyword other than the default search provider.  If the user types a keyword (which also applies to tab-to-search) in the omnibox this qualifier is applied to the transition type of the generated url.  An additional visit with a transition type of KEYWORD_GENERATED may then be generated against the url 'http://' + keyword.  For example, if the user does a tab-to-search against wikipedia the generated url has a transition qualifer of KEYWORD and a visit for 'wikipedia.org' is also generated with a transition type of KEYWORD_GENERATED."),
                     ("KEYWORD_GENERATED", "Corresponds to a visit generated for a keyword.  See description of KEYWORD for more details.")]

class HistoryItem(object):
   url = ""
   tab_header = ""
   visit_count = -1
   typed_count = -1
   last_visit_time = -1
   hidden = -1
   visit_time = -1
   from_visit = -1
   transition = -1

   # class function that initializes new Vuln object
   def __init__(self, url, tab_header, visit_count, typed_count, last_visit_time, hidden, visit_time, from_visit, transition):
      self.url = url
      self.tab_header = tab_header
      self.visit_count = visit_count
      self.typed_count = typed_count
      self.last_visit_time = last_visit_time
      self.hidden = hidden
      self.visit_time = visit_time
      self.from_visit = from_visit
      self.transition = transition

   # function that prints history item attributes
   def print_HistoryItem(self):
      print("              URL:             " + str(self.url))
      print("              Tab header:      " + str(self.tab_header))
      print("              Visit count:     " + str(self.visit_count))
      print("              Typed count:     " + str(self.typed_count))
      print("              Last visit time: " + str(self.last_visit_time))
      print("              Hidden:          " + str(self.hidden))
      print("              Visit time:      " + str(self.visit_time))
      print("              From visit:      " + str(self.from_visit))
      print("              Transition:      " + " - ".join(page_transitions[self.transition]))
      print()

# function external to the HistoryItem class that initializes new HistoryItem object
def create_HistoryItem(url, tab_header, visit_count, typed_count, last_visit_time, hidden, visit_time, from_visit, transition):
   return HistoryItem(url, tab_header, visit_count, typed_count, last_visit_time, hidden, visit_time, from_visit, transition)

def db_fetch(username):
   sqlite_file = 'C:\\Users\\' + username + '\\AppData\Local\Google\Chrome\\User Data\Default\History'

   try:
      conn = sqlite3.connect(sqlite_file)
      c = conn.cursor()
      # https://stackoverflow.com/questions/31986520/show-tables-in-sqlite-database-in-python
      c.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
      all_rows = c.fetchall()

      c.execute("SELECT urls.url, urls.title, urls.visit_count, urls.typed_count, datetime(((urls.last_visit_time - 11644473600000000)/1000000),'unixepoch','localtime') as last_visit, urls.hidden, datetime(((visits.visit_time - 11644473600000000)/1000000),'unixepoch','localtime') as visit_time, visits.from_visit, visits.transition FROM urls, visits WHERE urls.id = visits.url")
      query = c.fetchall()
   except:
      print("Unable to open database file for " + username)
      return False

   return query

def pull_history(query):
   history = {}
   # bar = Bar('Processing Chrome history...                          ', fill='=', max=len(query))
   for line in tqdm(range(0, len(query))):
      # https://stackoverflow.com/questions/36402056/google-chrome-how-to-find-out-the-name-of-transition-from-its-id-in-history-sql
      history_item = create_HistoryItem(query[line][0], query[line][1], query[line][2], query[line][3], datetime.strptime(query[line][4], "%Y-%m-%d %H:%M:%S"), query[line][5], datetime.strptime(query[line][6], "%Y-%m-%d %H:%M:%S"), query[line][7], query[line][8] & 0xFF)
      history[int(history_item.last_visit_time.timestamp())] = history_item
      # bar.next()
   # bar.finish()

   # https://stackoverflow.com/questions/403421/how-to-sort-a-list-of-objects-based-on-an-attribute-of-the-objects
   # history.sort(key=lambda x: x.last_visit_time, reverse=True)

   return history

def main():
   username = input("Query Chrome history for which username? ")
   query = db_fetch(username)
   chrome_history = pull_history(query)

   for time in chrome_history:
      chrome_history[time].print_HistoryItem()

   return chrome_history

if __name__ == '__main__':
   main()