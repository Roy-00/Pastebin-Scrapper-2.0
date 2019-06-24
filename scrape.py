import requests
import sys
import json
import os
import datetime
from time import sleep

class PasteBin_Keyword_Scrapper():
    def __init__(self):
        self.keywords_filename = sys.argv[1]        # Location of the keywords file.
        self.key_set = set()                        # Keeps track of the keys of all pastes scrapped during a single execution.
        self.current_date = datetime.datetime.now() # Today's date and time, default formatting.

    def get_keywords(self):
        with open(self.keywords_filename,"r") as keyword_file:
            self.keywords_list = keyword_file.read().splitlines() # Read keywords and store each keyword in a list.
            # print(self.keywords_list)                           # For debugging. Shows current keywords each time this function is called.

    def get_pastes(self):
        scrape = requests.get("https://scrape.pastebin.com/api_scraping.php?limit=100")
        if scrape.status_code == 200:         # Successful scrape of 100 pastes.
            self.parsed_json = "Blank"        # Instantiate self.parsed_json.
            try:                              # Try extracting the json out of the scrape request.
                self.parsed_json = scrape.json()
            except:                           # Failed json extraction.
                print("Request failed.")
                current_datetime = self.current_date.strftime("%m-%d-%YT") + self.current_date.strftime("%H:%M:%S") # Today's date and time, formatted as shown.
                current_monthyear = self.current_date.strftime("%m-%Y") # Today's month and year.
                try: # Create folder for the current month of scrapping if not already created.
                    if not os.path.exists("pastes/" + current_monthyear):
                        os.makedirs("pastes/" + current_monthyear)
                except OSError: # Failure to create such folder.
                    print ('Error: Creating directory - ' +  "pastes/" + current_monthyear)
                with open("pastes/" + current_monthyear + "/fail_" + current_datetime + ".txt","w") as file: # Log error to file.
                    file.write(scrape.text)   # If there is a rate limit exceeded or whatever text is in the request object, that will be written to file.
                print(sys.exc_info()[0])      # Print error to console.
        else:
            print("ERROR calling the URL.\n") # Perhap's Pastebin is down? Error contacting Pastebin regardless.
            self.parsed_json = scrape.json()  # Push whatever json may be in the request object into self.parsed_json just to see if there is anything of value in there.

    def iterate_pastes(self):
        for paste in self.parsed_json:  # Iterate through the pastes in self.parsed_json.
            self.paste = paste
            scrape_url = requests.get(self.paste['scrape_url']) # Request the text within the paste through the scarpe_url of the paste.
            self.text = scrape_url.text
            self.check_key_set()
        # print(self.key_set)   # For debugging. Shows key_set at the end of the loop above.

    def check_key_set(self):
        if self.paste['key'] not in self.key_set: # No duplicate paste present.
            self.key_set.add(self.paste['key'])   # Add key of paste into key_set.
            self.check_keywords()
        else:                                     # Duplicate paste present, don't check for keywords.
            return

    def check_keywords(self):
        for word in self.keywords_list: # Iterate through keywords in keyword file.
            if word.lower() in self.text.lower(): # Keyword present.
                print("*** HIT ***")
                current_monthyear = self.current_date.strftime("%m-%Y")
                try: # Create folder for the current month of scrapping if not already created.
                    if not os.path.exists("pastes/" + current_monthyear):
                        os.makedirs("pastes/" + current_monthyear)
                except OSError: # Failure to create such folder.
                    print ('Error: Creating directory - ' +  "pastes/" + current_monthyear)
                file_name = "pastes/" + current_monthyear + "/"+ str(self.paste['key']) + ".txt"
                text = self.text
                try: # Try to see if we can write paste to local file as string.
                    with open(file_name,"w") as paste_file:
                        paste_file.write(str(text))
                    print(str(self.paste['key']))
                    print("String:")
                    print("============================")
                    print(str(text))
                    print("============================")
                except: # Write paste to local file as bytes, else fail.
                    with open(file_name,"wb") as paste_file:
                        paste_file.write(text.encode("utf-8"))
                    print(str(self.paste['key']))
                    print("Bytes:")
                    print("============================")
                    print(text.encode("utf-8"))
                    print("============================")

def main():
    PBSobj = PasteBin_Keyword_Scrapper()     # instantiate scraping class.
    for i in range(0,10):                    # Loop 10 times, 100 pastes scrapped each time.
        print("Scanning 100 most recent pastes from Pastebin.")
        PBSobj.get_keywords()
        PBSobj.get_pastes()
        PBSobj.iterate_pastes()
        sleep(60)                            # Scraping limit: 1000 pastes scrapped per 10 minutes max.
    print("1000 pastes have been scanned.")  # Heppy.

if __name__ == '__main__':                   # Start here.
    main()
