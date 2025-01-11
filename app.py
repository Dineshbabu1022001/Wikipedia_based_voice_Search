import pyttsx3
import wikipedia as wp
from flask import Flask, render_template, request, flash, redirect, url_for
import threading
import multiprocessing

app = Flask(__name__)
app.secret_key = "supersecretkey"  # Necessary for flash messages

# Global variables to handle the speech process
speech_process = None

# Function to search Wikipedia and return result
def search_wikipedia(topic, sentences):
    try:
        n = int(sentences)
        if n <= 0:
            return "Please enter a positive number for sentences."
        result = wp.summary(topic, sentences=n)
        return result
    except ValueError:
        return "Invalid number of sentences entered."
    except wp.DisambiguationError as e:
        return f"Ambiguous search query. Please be more specific.\n\nOptions:\n{', '.join(e.options)}"
    except wp.PageError:
        return "No matching page found on Wikipedia."
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Voice function that will run in a separate process
def perform_audio(result):
    voice = pyttsx3.init()
    voice.setProperty('rate', 150)  # Speed of the speech
    voice.say(result)
    voice.runAndWait()

# Stop function to kill the speech process
def stop_audio():
    global speech_process
    if speech_process and speech_process.is_alive():
        speech_process.terminate()
        speech_process.join()

# Flask routes
@app.route("/", methods=["GET", "POST"])
def home():
    global speech_process

    if request.method == "POST":
        if 'stop' in request.form:
            stop_audio()
            return render_template("index.html", result=None, stop_status="Audio stopped.")
        
        topic = request.form["topic"]
        sentences = request.form["sentences"]
        
        # Validate inputs
        if not topic or not sentences:
            flash("Both fields are required!", "error")
            return redirect(url_for("home"))
        
        result = search_wikipedia(topic, sentences)

        # Start the audio in a separate process
        speech_process = multiprocessing.Process(target=perform_audio, args=(result,))
        speech_process.start()

        return render_template("index.html", result=result)

    return render_template("index.html", result=None)

if __name__ == "__main__":
    app.run(debug=True)