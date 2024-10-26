import speech_recognition as sr
from googletrans import Translator

def translate_audio(file_path, target_language='en'):
    r = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        try:
            audio_text = r.listen(source)
            text = r.recognize_google(audio_text)
            print('Converting audio transcripts into text ...')
            print('Original Text:', text)

            translator = Translator()
            translation = translator.translate(text, dest=target_language, src='auto')
            print('Translated Text:', translation.text)

            return translation.text

        except sr.UnknownValueError:
            print('Speech Recognition could not understand the audio.')
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")

