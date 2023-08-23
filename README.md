# anki-automation
:warning: **DISCLAIMER:** This code was rapidly developed for personal use. It may lack documentation, tests, and best practices. Use at your own risk.

Scrapes information from MnemonicDictionary, uses gTTS to generate audio files, and compiles into an Anki deck. The [GRE Word List](https://mnemonicdictionary.com/wordlist/GREwordlist) was scraped, and the resulting Anki ```.apkg``` is included.

Note that gTTS eventually throws a 429 Too Many Requests, but I got past it with a VPN. An alternative would be to use [Google Cloud](https://cloud.google.com/text-to-speech) for text-to-speech instead.
