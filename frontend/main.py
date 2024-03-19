import gradio as gr

def transcribe_audio(audio):
    # Code to transcribe the audio input
    # ...
    return "Transcribed text"

audio_input = gr.Audio()
interface = gr.Interface(fn=transcribe_audio, inputs=audio_input, outputs="text")
interface.launch()