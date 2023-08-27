# anki-automation
:warning: **DISCLAIMER:** This code was rapidly developed for personal use. It may lack documentation, tests, and best practices. Use at your own risk.

Scrapes information from MnemonicDictionary, gets their definitions using [freeDictionaryAPI](https://github.com/meetDeveloper/freeDictionaryAPI) for Google's dictionary, uses gTTS to generate audio files, and compiles into an Anki deck. The [GRE Word List](https://mnemonicdictionary.com/wordlist/GREwordlist) was scraped, and the resulting Anki ```.apkg``` is included.

Note that gTTS eventually throws a 429 Too Many Requests, but I got past it with a VPN. An alternative, more robust solution would be to use [Google Cloud](https://cloud.google.com/text-to-speech) for text-to-speech instead.

`main.py` can be run from the command line: `python main.py`. Python 3.11 was used for testing.

`main_legacy.py` was used when the definitions were obtained directly from MnemonicDictionary. The quality of the definitions were not optimal, so I switched to the definition you get when you Google "[word] definition".
