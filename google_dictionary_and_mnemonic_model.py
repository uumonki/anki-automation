import genanki

google_dictionary_and_mnemonic_model = genanki.Model(
    model_id=2020180200,
    name="Mnemonic Dictionary Model with Audio",
    fields=[
        {"name": "Word"},
        {"name": "Explanation"},
        {"name": "Mnemonic Hints"},
        {"name": "Audio"},
    ],
    templates=[
        {
            "name": "Card",
            "qfmt": "{{Audio}} &nbsp; {{Word}}",
            "afmt": """
                    <center><h2>{{Word}}</h2></center>
                    {{Explanation}}
                    <hr>
                    <b>Mnemonic Hints:</b><br>
                    {{Mnemonic Hints}}<br>
                    """,
        },
    ],
    css="""
        .card {
            font-family: arial;
            font-size: 20px;
            text-align: left;
            color: black;
            background-color: white;
            margin: 20px;
            padding: 20px;
            border-radius: 15px;
            box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
        }
        h2 {
            color: darkred;
            border-bottom: 2px solid gray;
            padding-bottom: 5px;
            margin-bottom: 20px;
        }
        ul { margin: 0; }
        hr { margin: 25px 0; }
        .explanation > div { margin-bottom: 20px; }
        .explanation > div:last-child { margin-bottom: 0; }
        .spaced { margin-top: 5px; }
        .syn {
            display: inline;
            color: dodgerblue;
        }
        .example { color: darkblue; }
        .hint { color: darkgreen; }
        """,
)
