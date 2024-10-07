# Determine_Fame.py

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import pandas as pd
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.edge.service import Service as EdgeService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.edge.options import Options as EdgeOptions
import time
import unicodedata

# Initialize global variables
artists_data = pd.DataFrame()
artists, artists_fame, unavailable_artists = [], [], []
unique_artists = {}
driver = None  # Initialize driver as None

def clean_string(text):
    nfkd_string = unicodedata.normalize("NFKD", str(text))
    text = "".join([c for c in nfkd_string if not unicodedata.combining(c)])
    return text

def cosine_sim_vectors(v1, v2):
    v1 = v1.reshape(1, -1)
    v2 = v2.reshape(1, -1)
    return cosine_similarity(v1, v2)[0][0]

def name_similarity(text1, text2):
    text1 = clean_string(text1)
    text2 = clean_string(text2)
    vector = CountVectorizer().fit_transform([text1, text2])
    return cosine_sim_vectors(vector[0], vector[1])

def initialize_driver(platform):
    global driver
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--headless")
    
    edge_options = EdgeOptions()
    edge_options.add_argument("--headless")
    
    try:
        if name_similarity(platform, "chrome") > 0.6:
            service = ChromeService(ChromeDriverManager().install())
            driver = webdriver.Chrome(service=service, options=chrome_options)
        elif name_similarity(platform, "firefox") > 0.6:
            service = FirefoxService(GeckoDriverManager().install())
            driver = webdriver.Firefox(service=service, options=firefox_options)
        elif name_similarity(platform, "microsoft edge") > 0.4:
            service = EdgeService(EdgeChromiumDriverManager().install())
            driver = webdriver.Edge(service=service, options=edge_options)
        driver.implicitly_wait(10)
        print(f"{platform.capitalize()} driver initialized successfully.")
    except Exception as e:
        print(f"Error initializing driver: {e}")
        driver = None

def close_driver():
    global driver
    if driver:
        driver.quit()
        driver = None
        print("WebDriver closed successfully.")

def artsy_link(artist):
    name = clean_string(artist)
    print(f"Artist: {artist} ({name})")
    name = "-".join(name.lower().split())
    url = "https://artsy.net/artist/" + name
    return url

def artsy_search_link(artist):
    try:
        driver.get("https://artsy.net/artists/")
        search = driver.find_element("xpath", "//input[@class='Input__StyledInput-bysdh7-0 gFWniP']")
        search.send_keys(artist)
        time.sleep(2)
        results_list = driver.find_element("xpath", "//ul[@class='react-autosuggest__suggestions-list']")
        iteration = 0
        highest_similarity, highest_iteration = 0, 0
        try:
            result = results_list.find_element("xpath", f".//li[@data-suggestion-index='{iteration}']")
            while result:
                iteration += 1
                result = results_list.find_element("xpath", f".//li[@data-suggestion-index='{iteration}']")
                result_type = result.find_element("xpath", ".//div[@class='Box-sc-15se88d-0 Text-sc-18gcpao-0 caIGcn wvERG']").text
                result_name = result.find_element("xpath", ".//div[@class='Box-sc-15se88d-0 Text-sc-18gcpao-0  dYxhVR']").text
                if result_type.lower() == "artist":
                    similarity = name_similarity(artist, result_name)
                    print(f"{artist}: ({result_name} = {similarity})")
                    if similarity > highest_similarity:
                        highest_similarity = similarity
                        highest_iteration = iteration
        except selenium.common.exceptions.NoSuchElementException:
            if highest_similarity >= 0.6:
                artist_result = driver.find_element("xpath", f"//li[@data-suggestion-index='{highest_iteration}']")
                artist_link = artist_result.find_element("xpath", ".//a[@class='RouterLink__RouterAwareLink-sc-1nwbtp5-0 bwxvKP SuggestionItem__SuggestionItemLink-sc-1ivuich-0 bssCjZ']").get_attribute("href")
                return artist_link
            else:
                return ""
    except Exception as e:
        print(f"Error during artsy_search_link: {e}")
        return ""

def biography_artsy(artist, driver):
    links = [artsy_link, artsy_search_link]
    for num_link in range(len(links)):
        link = links[num_link](artist)
        if len(link) == 0:
            break
        driver.get(link)
        try:
            driver.find_element("xpath", "//div[@class='Box-sc-15se88d-0 Text-sc-18gcpao-0  bTXFzS']")
            continue
        except selenium.common.exceptions.NoSuchElementException:
            try:
                expand_bio = driver.find_element("xpath", "//button[@class='Clickable-sc-10cr82y-0 dgMPBb']")
                expand_bio.click()
                biography = driver.find_element("xpath", "//div[@class='ReadMore__Container-sc-1bqy0ya-0 hSZzlP']").text
                return biography
            except selenium.common.exceptions.NoSuchElementException:
                return ""
    unavailable_artists.append(artist)
    print(f"{artist} unavailable")
    return ""

def generate_fame_data(platform):
    initialize_driver(platform)
    if driver:
        # Load your dataset here if needed
        # artists_data = pd.read_csv("artDataset.csv")
        # artists = artists_data["artist"].tolist()
        # Implement bulk fame generation if necessary
        close_driver()
    else:
        print("Driver initialization failed. Fame data not generated.")

def get_fame(artist):
    """
    Initialize the driver, fetch the biography, compute fame, and close the driver.
    Returns the fame score (integer).
    """
    platform = "chrome"  # You can modify this to choose different browsers if needed
    initialize_driver(platform)
    if driver:
        try:
            biography = biography_artsy(str(artist), driver)
            fame = len(biography.split()) if biography else 0
            print(f"Fame for {artist}: {fame}")
            return fame
        except Exception as e:
            print(f"Error getting fame for {artist}: {e}")
            return 0
        finally:
            close_driver()
    else:
        print("Driver not initialized. Cannot get fame.")
        return 0

# Optionally, you can have a function to pre-generate fame data for all artists
def generate_artist_fame():
    for artist in artists:
        if artist not in unique_artists:
            biography = biography_artsy(artist, driver)
            fame = len(biography.split()) if biography else 0
            artists_fame.append(fame)
            unique_artists[artist] = fame
        else:
            artists_fame.append(unique_artists[artist])

    with open("unavailable_artists.txt", "w") as unavailable_artists_file:
        unavailable_artists_file.write(str(unavailable_artists))
    
    while len(artists_fame) < len(artists_data):
        artists_fame.append(None)
    
    artists_data.insert(artists_data.columns.get_loc("artist") + 1, "fame", artists_fame)
    artists_data.to_csv("artist_fame.csv", index=False)
