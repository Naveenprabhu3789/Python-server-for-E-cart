from flask import Flask, request, jsonify
from audioRecorder import AudioRecorder
from speechTranslator import translate_audio
import google.generativeai as genai
import PIL.Image
import os
import logging
import socket

app = Flask(__name__)
recorder = AudioRecorder()

# Configure Gemini AI once for the entire application
genai.configure(api_key="AIzaSyBxqos-ABArpNayKu-h5r06BqZdDwUR0F4")  # Replace with your actual API key

logging.basicConfig(level=logging.DEBUG)

@app.route('/start_recording')
def start_recording():
    recorder.start_recording()
    return "Recording started."

@app.route('/stop_recording')
def stop_recording():
    recorder.stop_recording()
    translated_text = translate_audio('record.wav')
    return f"Recording stopped. Translated Text: {translated_text}"

# New route for image processing
@app.route('/process_image', methods=['GET', 'POST'])
def process_image():
    logging.debug(f"Received request to /process_image")
    
    # Use a test image path
    temp_image_path = '/home/naveen/Downloads/ondc_server/images.jpeg'
    
    logging.debug(f"Full image path: {os.path.abspath(temp_image_path)}")
    
    # Check if the image file exists
    if not os.path.exists(temp_image_path):
        error_msg = f"Test image not found at {temp_image_path}"
        logging.error(error_msg)
        return error_msg, 400
    
    # Check read permissions for the image file
    if not os.access(temp_image_path, os.R_OK):
        error_msg = f"No read permission for image file: {temp_image_path}"
        logging.error(error_msg)
        return error_msg, 403
    
    try:
        img = PIL.Image.open(temp_image_path)
        logging.debug(f"Successfully opened image: {temp_image_path}")
    except Exception as e:
        error_msg = f"Error opening image: {str(e)}"
        logging.error(error_msg)
        return error_msg, 400

    # Update the model name
    model = genai.GenerativeModel(model_name="gemini-1.5-flash")
    try:
        response = model.generate_content(["What is in this image?", img])
        logging.debug("Successfully generated content from image")
    except Exception as e:
        error_msg = f"Error generating content: {str(e)}"
        logging.error(error_msg)
        return error_msg, 500

    # Define output directory and file
    output_dir = '/home/naveen/Downloads/ondc_server/output'
    output_file = os.path.join(output_dir, 'image_analysis_result.txt')
    
    logging.debug(f"Full output directory path: {os.path.abspath(output_dir)}")
    logging.debug(f"Full output file path: {os.path.abspath(output_file)}")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Check write permissions for the output directory
    if not os.access(output_dir, os.W_OK):
        error_msg = f"No write permission for output directory: {output_dir}"
        logging.error(error_msg)
        return error_msg, 403
    
    # Save the response to a file
    try:
        with open(output_file, 'w') as f:
            f.write(response.text)
        logging.debug(f"Successfully wrote response to {output_file}")
    except Exception as e:
        error_msg = f"Error writing to file: {str(e)}"
        logging.error(error_msg)
        return error_msg, 500
    
    return jsonify({"response": response.text, "output_file": output_file})

print(f"Attempting to run on {socket.gethostname()}:5000")

if __name__ == '__main__':
    try:
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting the Flask app: {e}")
