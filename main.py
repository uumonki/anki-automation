import os
import time
import html
import genanki
from gtts import gTTS
import requests
from model import mnemonic_model
from bs4 import BeautifulSoup

# import webbrowser

# words to filter out of mnemonic hints (i don't speak hindi)
filter_words = ["hindi"]


# Generate audio function
def generate_audio(word, filename):
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


# Function to scrape a page and create Anki cards
def scrape_and_create_cards(url, deck):
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
        short_def = div.find("p", recursive=False).text.split(":")[1].strip()

        enclosing_div = div.find("div", recursive=False)
        parts = str(enclosing_div).split("<u>Definition</u>")
        explanation = '<div class="explanation">'

        for part in parts[1:]:
            explanation += "<div>"
            part_soup = BeautifulSoup(part, "lxml")

            definition = part_soup.find("br").next_sibling.strip()
            explanation += "<b>Definition &nbsp;</b>" + definition + "<br>"

            synonyms = [
                '<p class="syn">' + a.text.strip() + "</p>"
                for a in part_soup.find_all("a")
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

        hint_texts = []
        for card_text_div in div.find_all("div", class_="card-text"):
            p = card_text_div.find_all("p")[-1]
            p_text = p.text.strip()
            if not any([word in p_text.lower() for word in filter_words]):
                hint_texts.append(html.escape(p_text))

        hints = "<ul>"
        for hint_text in hint_texts[:5]:
            hints += f'<li class="hint">{hint_text}</li>'
        hints += "</ul>"

        audio_filename = generate_audio(word, f"{word}.mp3")

        note = genanki.Note(
            model=mnemonic_model,
            fields=[
                word,
                short_def,
                explanation,
                hints,
                f"[sound:{audio_filename}]",
            ],
        )
        deck.add_note(note)


def main():
    deck = genanki.Deck(deck_id=1076326919, name="Mnemonic Dictionary Deck")

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
