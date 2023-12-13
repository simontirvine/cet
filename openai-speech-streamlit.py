#################################
# Import libraries and packages #
#################################

import streamlit as st
import os
import azure.cognitiveservices.speech as speechsdk
import openai

#############################
# Marketing stuff goes here #
#############################

st.image('https://irelandinc.com/wp-content/uploads/sites/6/2019/03/Kpmg-logo.png', width=150)

st.title('Virtual Chief Digital Officer')

st.write('Welcome to your AI-powered CDO speechbot - developed using Microsoft Azure and OpenAI.')

#################################
# Azure Cognitive Services Load #
#################################

os.environ['OPEN_AI_KEY'] = '4832a84a39184c4581084c832e49400f'
os.environ['OPEN_AI_ENDPOINT'] = 'https://et-openai-service.openai.azure.com/'
os.environ['SPEECH_KEY'] = '205a42d5f6954bc3b45f0a6332c53c53'
os.environ['SPEECH_REGION'] = 'eastus'

# This example requires environment variables named "OPEN_AI_KEY" and "OPEN_AI_ENDPOINT"
# Your endpoint should look like the following https://YOUR_OPEN_AI_RESOURCE_NAME.openai.azure.com/
openai.api_key = os.environ.get('OPEN_AI_KEY')
openai.api_base =  os.environ.get('OPEN_AI_ENDPOINT')
openai.api_type = 'azure'
openai.api_version = '2022-12-01'

#################################
# Pre-loaded prompts for OpenAI #
#################################

prompt_ai = "You are an KPMG chatbot and your name is Fahad Ibn Abdullah and your primary goal is to welcome this esteemed audience and answer general  queries. \n•\tProvide concise replies (20 words or less) that are polite and professional. If you are asked to tell a joke, tell a joke about AI or data. \n•\tAnswer questions truthfully based on official information.\n•\tDo not answer questions that are not related to emerging technology and innovation in Saudi Arabia and respond with \"I can only help questions you may have about AI in Saudi Arabia.\". \n•\tIf you do not know the answer to a question, respond by saying “I do not know the answer to your question. Why don't you catch one of the good people here, who may be able to help you.”  \n•\tKPMG and Microsoft have an alliance:\n•\tKPMG and Microsoft combine advanced technologies, industry insight, creative thinking, and established excellence in advising on complex global business issues to help transform your company in the areas most critical to your prosperity and ongoing sustainable success. As your organization expands to new geographies, develops new products and recruits new talent, processes can become increasingly complex and harder to scale. Market forces, such as evolving data protection laws, currency fluctuations and geopolitical tensions, increase the complexity and require a greater responsiveness for systems and tools.\n\n•\tThe strong portfolio of KPMG and Microsoft alliance offerings can help you address these challenges by building applications on demand, automating manual processes, and continuously analyzing information to help reduce the risk of errors and increase your ability to make smart decisions. As you embark on your digital transformation journey, you can rely on KPMG professionals and our business-first approach to deliver effective Microsoft technology-based solutions to help you achieve meaningful and sustainable business outcomes.\n•\tDeveloping an AI-enabled application development and knowledge platform on Microsoft Azure will expedite the creation of specialized solutions for clients, helping to enhance their competitive advantage and profitability while putting ethics and security at the very core of the offerings. "

prompt_cdo = "You are the virtual Chief Digital Officer (or CDO) at KPMG and your name is Fahad Ibn Abdullah and your primary goal is to welcome this esteemed audience and answer general queries about emerging digitial technologies such as the metaverse, blockchain, AI, machine learning, process automation and quantum computing. Provide concise replies (20 words or less) that are polite and  professional. If you are asked to tell a joke, tell a joke about emerging tech, AI, machine learning, automation, IoT.  Answer questions truthfully based on official information.  Do not answer questions that are not related to emerging and advanced technologies and respond with I can only help questions you may have about emerging tech and their role in Saudi Arabia.  If you do not know the answer to a question, respond by saying  I do not know the answer to your question. Why don't you catch one of the good people here, who may be able to help you. Chief digital officers oversee the adoption of digital technologies across an organization, transforming business strategy using technology and data, and evangelizing how people, processes, and technology can enable that digital vision. Sense the opportunities of emerging digital technologies and digital-enabled business models. CDOs do the following: Build and maintain external relationships with vendors, startups, analysts, and academia and be part of relevant ecosystems. Act as a thought leader who articulates the digital future of the enterprise. Educate the board on digital, building tech fluency from the top down. Ensure the business strategy is a digital strategy. Lead the development of the digital capabilities necessary for digital transformation throughout the enterprise. Drive the move toward an insight-driven organization that leverages the power of data. Build digital talent in the organization through a combination of developing current staff and attracting new talent. Champion the process to identify, trial, evaluate, and scale or fail new digital technologies while ensuring they are relevant to the business. Oversee the execution of digital initiatives"

message_text = prompt_cdo

##########################################
# Load OpenAI model and configure speech #
##########################################

# This will correspond to the custom name you chose for your deployment when you deployed a model.
deployment_id='gpt-35-turbo-instruct' 

# This example requires environment variables named "SPEECH_KEY" and "SPEECH_REGION"
speech_config = speechsdk.SpeechConfig(subscription=os.environ.get('SPEECH_KEY'), region=os.environ.get('SPEECH_REGION'))
audio_output_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

# Should be the locale for the speaker's language.
speech_config.speech_recognition_language="en-GB"
speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

# The language of the voice that responds on behalf of Azure OpenAI.
speech_config.speech_synthesis_voice_name='en-GB-RyanNeural'
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_output_config)

# tts sentence end mark
tts_sentence_end = [ ".", "!", "?", ";", "。", "！", "？", "；", "\n" ]

################################
# Buttons and actions are here #
################################

start = st.button("Start conversation")
if start == True:
    st.write('I am listening to you. Go ahead and talk to me.')

############################################
# Run the STT and TTS model through OpenAI #
############################################

    # Prompts Azure OpenAI with a request and synthesizes the response.
    def ask_openai(prompt):
        # Ask Azure OpenAI in streaming way
        response = openai.Completion.create(engine=deployment_id, prompt=prompt, max_tokens=200, stream=True)
        collected_messages = []
        last_tts_request = None

        # iterate through the stream response stream
        for chunk in response:
            if len(chunk['choices']) > 0:
                chunk_message = chunk['choices'][0]['text']  # extract the message
                collected_messages.append(chunk_message)  # save the message
                if chunk_message in tts_sentence_end: # sentence end found
                    text = ''.join(collected_messages).strip() # join the recieved message together to build a sentence
                    if text != '': # if sentence only have \n or space, we could skip
                        print(f"Speech synthesized to speaker for: {text}")
                        last_tts_request = speech_synthesizer.speak_text_async(text)
                        collected_messages.clear()
        if last_tts_request:
            last_tts_request.get()

    # Continuously listens for speech input to recognize and send as text to Azure OpenAI
    def chat_with_open_ai():
        while True:
            print("Azure OpenAI is listening. Say 'Stop' or press Ctrl-Z to end the conversation.")
            try:
                # Get audio from the microphone and then send it to the TTS service.
                speech_recognition_result = speech_recognizer.recognize_once_async().get()

                # If speech is recognized, send it to Azure OpenAI and listen for the response.
                if speech_recognition_result.reason == speechsdk.ResultReason.RecognizedSpeech:
                    if speech_recognition_result.text == "Stop.": 
                        print("Conversation ended.")
                        break
                    print("Recognized speech: {}".format(speech_recognition_result.text))
                    speech_processed = message_text + speech_recognition_result.text
                    ask_openai(speech_processed)
                    #ask_openai(speech_recognition_result.text)
                elif speech_recognition_result.reason == speechsdk.ResultReason.NoMatch:
                    print("No speech could be recognized: {}".format(speech_recognition_result.no_match_details))
                    break
                elif speech_recognition_result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = speech_recognition_result.cancellation_details
                    print("Speech Recognition canceled: {}".format(cancellation_details.reason))
                    if cancellation_details.reason == speechsdk.CancellationReason.Error:
                        print("Error details: {}".format(cancellation_details.error_details))
            except EOFError:
                break

    # Main

    try:
        chat_with_open_ai()
    except Exception as err:
        print("Encountered exception. {}".format(err))

