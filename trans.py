"""
English to Kannada Translator
==============================
A simple command-line tool that translates English phrases into Kannada.
Uses the 'deep-translator' library (pip install deep-translator).
"""

from deep_translator import GoogleTranslator


def translate_to_kannada(english_text: str) -> str:
    """
    Translates an English string to Kannada.

    Args:
        english_text: The English phrase or sentence to translate.

    Returns:
        The translated Kannada text as a string.
    """
    translator = GoogleTranslator(source="en", target="kn")
    translated = translator.translate(english_text)
    return translated


def main():
    print("=" * 50)
    print("   English → Kannada Translator")
    print("=" * 50)
    print("Type 'quit' or 'exit' to stop the program.\n")

    while True:
        # Get input from the user
        english_input = input("Enter English text: ").strip()

        # Allow the user to exit
        if english_input.lower() in ("quit", "exit", ""):
            print("Goodbye! / ವಿದಾಯ!")
            break

        try:
            kannada_output = translate_to_kannada(english_input)
            print(f"Kannada translation : {kannada_output}\n")
        except Exception as e:
            print(f"[Error] Could not translate. Details: {e}\n")


if __name__ == "__main__":
    main()