from datetime import datetime
from logging.config import listen
import speech_recognition as sr
import pyttsx3
import webbrowser
import wikipedia
import wolframalpha
import wolframclient
import pyaudio

# Speech engine initialisation
engine = pyttsx3.init()  # creeaza o referinta catre instanta pyttsx3.Engine
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)  # 0 =  barbat, 1 = femeie
activationWord = 'computer'  # Asteapta cuvantul "computer" pentru a porni, similar cu Alexa n Google

# Configuram Browserul

chrome_path = r"C:\Users\Calin-Victor Iorga\AppData\Local\Google\Chrome\Application\chrome.exe"
webbrowser.register('chrome_path', None, webbrowser.BackgroundBrowser(chrome_path))

# Wolfram Alpha Client
appId = '4A97GH-PJQUUJ4EXE'
wolframClient = wolframalpha.Client(appId)

def parseCommand():
    listener = sr.Recognizer()  # creeaza o instanta a clasei Recognizer
    print("Listening for a command")

    with sr.Microphone() as source: # foloseste microfonul default ca sursa audio
        listener.pause_threshold = 2 # Represents the minimum length of silence (in seconds) that will register as the end of a phrase
        input_speech = listener.listen(source) # salveaza inputul din microfon intr-o variabila

    try:
        print('Recognizing speech...')
        query = listener.recognize_google(input_speech, language = 'en_gb') # API Google Speech Recognition
        print(f'The input speech was: {query}')
    except Exception as exception:
        print('I did not quite catch that')
        speak('I did not quite cach that')
        print(exception)
        return 'None'

    return query

def search_wikipedia(query = ''):
    searchResults = wikipedia.search(query) #cauta rezultate ale cautarii 'query' pe wikipedia
    if not searchResults:
        print('No wikipedia result')
        return 'No result received'
    try:
        wikiPage = wikipedia.page(searchResults[0]) # obtine un obiect Page al searchResult[0] reprezentand o pagina
    except wikipedia.DisambiguationError as error: # o clasa exceptie care este apelata atunci cand apar rezultate care ar putea avea legatura cu 'query' solicitat
        wikiPage = wikipedia.page(error.options[0]) #returneaza prima pagina aparuta ca optiune
    print(wikiPage.title)
    wikiSummary = str(wikiPage.summary) #returneaza sumarry-ul paginii
    return wikiSummary


def listOrDict(var):
    if isinstance(var, list):
        return var[0]['plaintext']
    else:
        return var['plaintext']

def search_wolframAlpha(query = ''):
    response = wolframClient.query(query) #asemenea cu functia search din modulul wiki, cauta 'query' prin motorul de cautare wolframAlpha
    # @success: Wolfram Alpha was able to resolve the query
    # @numpods: Number of results returned
    # pod: List of results. This can also contain subpods
    if response['@succes'] == 'false':
        return 'Could not compute'
    else:
        result = ''
        pod0 = response['pod'][0]
        pod1 = response['pod'][1]
        if (('result') in pod1['@title'].lower()) or (pod1.get('@primary', 'false') == 'true') or ('definition' in pod1['@title'].lower()):
            result = listOrDict(pod1['subpod'])
            return result.split('(')[0]
        else:
            question = listOrDict(pod0['subpod'])
            return question.split('(')[0]
            speak('Computation failed.')
            return search_wikipedia(question)

def speak(text = ''):
    engine.say(text)
    engine.runAndWait()

# Main Loop

if __name__ == '__main__':

    speak('Hello! I am an AI program made by Calin. Please, start speaking, I am listening')

    while True:
        query = parseCommand().lower().split()
        if query[0] == activationWord:
            query.pop(0)
            if query[0] == 'say':
                if 'hello' in query:
                    speak('Greetings, all.')
                else:
                    query.pop(0)
                    speech = ' '.join(query)
                    speak(speech)

            # Navigare
            if query[0] == 'go' and query[1] == 'to':
                speak('Opening...')
                query = ' '.join(query[2:])
                webbrowser.get('chrome').open_new(query)

            # Wikipedia
            if query[0] == 'wikipedia':
                query = ' '.join(query[1:])
                speak('Searching on wikipedia...')
                speak(search_wikipedia(query))

            # Wolfram Alpha
            if query[0] == 'compute' or query[0] == 'computer':
                query = ' '.join(query[1:])
                speak('Computing')
                try:
                    result = search_wolframAlpha(query)
                    speak(result)
                except:
                    speak('Unable to compute.')

            # Note taking
            if query[0] == 'log':
                speak('Ready to record your note')
                newNote = parseCommand().lower()
                now = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
                with open('note_%s.txt' % now, 'w') as newFile:
                    newFile.write(newNote)
                speak('Note written')

            if query[0] == 'exit':
                speak('Goodbye!')
                break

