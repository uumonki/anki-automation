import os
import time
import html
import genanki
from gtts import gTTS
import requests
from google_dictionary_and_mnemonic_model import google_dictionary_and_mnemonic_model
from bs4 import BeautifulSoup

# import webbrowser

# words to filter out of mnemonic hints (i don't speak hindi)
FILTER_WORDS = ["hindi"]


# Generate audio function
def generate_audio(word: str, filename: str) -> str:
    """Calls gTTS to generate an audio file for a word and saves it to filname.
    Returns the filename.
    """
    # first check if the file already exists
    if os.path.exists(filename):
        return filename
    tts = gTTS(text=word, lang="en")
    while True:
        try:
            tts.save(filename)
            break
        except Exception:
            # too many requests, wait for 10 seconds and try again
            print("Too many requests, waiting for 10 seconds...")
            time.sleep(10)
    return filename


def get_hints_from_div(div: BeautifulSoup) -> str:
    """Returns an HTML containing the mnemonic hints from a BeautifulSoup div object."""
    hint_texts = []
    for card_text_div in div.find_all("div", class_="card-text"):
        p = card_text_div.find_all("p")[-1]
        p_text = p.text.strip()
        if not any([word in p_text.lower() for word in FILTER_WORDS]):
            hint_texts.append(html.escape(p_text))

    hints = "<ul>"
    for hint_text in hint_texts[:5]:
        hints += f'<li class="hint">{hint_text}</li>'
    hints += "</ul>"


def get_google_dict_from_word(word: str) -> dict:
    """Calls https://github.com/meetDeveloper/freeDictionaryAPI to get the definition
    of a word.

    Raises:
        requests.exceptions.HTTPError: If the word is not found in the dictionary.
    """
    response = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
    response.raise_for_status()
    return response.json()[0]


def parse_google_dict(google_dict: dict) -> str:
    """Parses the response from get_google_dict_from_word() and returns a string
    containing the explanation in HTML.
    """
    explanation = '<div class="explanation">'
    if origin := google_dict.get("origin"):
        explanation += "<div>"
        explanation += "<b>Origin &nbsp;</b>" + origin + "<br>"
        explanation += "</div>"
    for meaning in google_dict["meanings"]:
        for definition in meaning["definitions"]:
            explanation += "<div>"
            explanation += (
                "<b>Definition &nbsp;</b>("
                + meaning["partOfSpeech"]
                + ") "
                + definition["definition"]
                + "<br>"
            )  # *Definition* (verb) ...
            if "example" in definition:
                explanation += "<b>Example &nbsp;</b>" + definition["example"] + "<br>"
            if "synonyms" in definition and definition.get("synonyms"):
                explanation += "<b>Synonyms &nbsp;</b>"
                for syn in definition["synonyms"]:
                    explanation += f'<span class="syn">{syn}</span>, '
                explanation = explanation[:-2] + "<br>"  # remove the last comma
            if "antonyms" in definition and definition.get("antonyms"):
                explanation += "<b>Antonyms &nbsp;</b>"
                for ant in definition["antonyms"]:
                    explanation += f'<span class="syn">{ant}</span>, '
                explanation = explanation[:-2] + "<br>"  # remove the last comma
            explanation += "</div>"
    explanation += "</div>"
    return explanation


def get_explanation_from_div(div: BeautifulSoup) -> str:
    """Returns an HTML containing the explanation from a BeautifulSoup div object.
    Note that though this is similar to the function in main_legacy.py, it includes
    additionally the short definition. Called when get_google_dict_from_word() fails.
    """
    short_def = div.find("p", recursive=False).text.split(":")[1].strip()
    enclosing_div = div.find("div", recursive=False)
    parts = str(enclosing_div).split("<u>Definition</u>")
    explanation = (
        f'<b>Short Definition:</b> {short_def}<br><hr><div class="explanation">'
    )

    for part in parts[1:]:
        explanation += "<div>"
        part_soup = BeautifulSoup(part, "lxml")

        definition = part_soup.find("br").next_sibling.strip()
        explanation += "<b>Definition &nbsp;</b>" + definition + "<br>"

        synonyms = [
            '<p class="syn">' + a.text.strip() + "</p>" for a in part_soup.find_all("a")
        ]
        if synonyms:
            explanation += "<b>Synonyms &nbsp;</b>" + ", ".join(synonyms) + "<br>"

        examples = [
            f'<li class="example">{li.text.strip()}</li>'
            for li in part_soup.find_all("li")
        ]
        if examples:
            explanation += (
                "<b>Example Sentences &nbsp;</b><ul>" + "".join(examples) + "</ul>"
            )
        explanation += "</div>"
    explanation += "</div>"
    return explanation


# Function to scrape a page and create Anki cards
def scrape_and_create_cards(url: str, deck: genanki.Deck) -> None:
    """Scrapes a page and creates Anki cards."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "lxml")
    # content = response.text
    # with open("temp.html", "w", encoding="utf-8") as f:
    #     f.write(content)
    # webbrowser.open("file://" + os.path.realpath("temp.html"))

    for div in soup.find_all(class_="mb-2 mt-2"):
        word_div = div.find("h2", recursive=False)
        if word_div is None:
            continue
        word = word_div.text

        try:
            explanation = parse_google_dict(get_google_dict_from_word(word))
        except requests.exceptions.HTTPError:
            explanation = get_explanation_from_div(div)
        hints = get_hints_from_div(div)
        audio_filename = generate_audio(word, f"{word}.mp3")

        note = genanki.Note(
            model=google_dictionary_and_mnemonic_model,
            fields=[
                word,
                explanation,
                hints,
                f"[sound:{audio_filename}]",
            ],
        )
        deck.add_note(note)


def main() -> None:
    deck = genanki.Deck(deck_id=1908808863, name="Mnemonic and Google Dictionary Deck")

    url = lambda x: f"https://mnemonicdictionary.com/wordlist/GREwordlist?page={x}"
    for i in range(1, 473):
        scrape_and_create_cards(url(i), deck)

    # Package everything into an Anki deck file
    media_files = [
        f for f in os.listdir() if f.endswith(".mp3")
    ]  # Collect all the mp3 files
    package = genanki.Package(deck)
    package.media_files = media_files
    package.write_to_file("mnemonic_deck.apkg")

    print("Deck has been created!")


if __name__ == "__main__":
    main()
