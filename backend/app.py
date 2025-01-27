from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from diffusers import StableDiffusionImg2ImgPipeline
from PIL import Image
import torch
import os

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Get the absolute path to the root directory (one level above the backend folder)
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Directories for uploaded and generated files
UPLOAD_FOLDER = os.path.join(ROOT_DIR, "uploads")
RESULTS_FOLDER = os.path.join(ROOT_DIR, "results")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULTS_FOLDER, exist_ok=True)

# Predefined rendering parameters
PRESETS = {
    "Futuristic": {"strength": 0.75, "guidance_scale": 7.5},
    "Modern Minimalism": {"strength": 0.6, "guidance_scale": 8.0},
    "Surrealism": {"strength": 0.9, "guidance_scale": 6.5},
}

# Global pipeline variable
img2img_pipe = None

def initialize_pipeline():
    """Initialize the pipeline globally."""
    global img2img_pipe
    try:
        device = "cpu"  # Use CPU for processing
        print(f"Using device: {device}")
        img2img_pipe = StableDiffusionImg2ImgPipeline.from_pretrained(
            "runwayml/stable-diffusion-v1-5",  # Updated model
            torch_dtype=torch.float32  # Float32 for CPU
        ).to(device)
        print("Pipeline initialized successfully!")
    except Exception as e:
        print(f"Error initializing pipeline: {e}")

# Call initialize_pipeline explicitly before starting the app
initialize_pipeline()

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # Validate that the uploaded file is an image
    if not file.content_type.startswith("image/"):
        return jsonify({"error": "Uploaded file is not an image"}), 400

    # Save the uploaded image to the 'uploads' folder
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    return jsonify({"message": "File uploaded successfully", "file_path": file_path})

@app.route('/generate', methods=['POST'])
def generate_image():
    global img2img_pipe
    if img2img_pipe is None:
        return jsonify({"error": "Pipeline is not initialized yet. Try again later."}), 500

    try:
        # Check for required fields in the request
        if 'prompt' not in request.form:
            return jsonify({"error": "No prompt provided"}), 400
        if 'preset' not in request.form:
            return jsonify({"error": "No preset provided"}), 400
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        # Retrieve inputs
        prompt = request.form['prompt']
        preset = request.form['preset']
        uploaded_image = request.files['image']

        # Validate preset
        if preset not in PRESETS:
            return jsonify({"error": f"Invalid preset: {preset}"}), 400

        # Get preset parameters
        preset_params = PRESETS[preset]
        strength = preset_params["strength"]
        guidance_scale = preset_params["guidance_scale"]

        # Save the uploaded image temporarily
        input_image_path = os.path.join(UPLOAD_FOLDER, "input_image.png")
        uploaded_image.save(input_image_path)
        print(f"Image saved at: {input_image_path}")

        # Load and preprocess the image
        init_image = Image.open(input_image_path).convert("RGB")
        init_image = init_image.resize((512, 512))  # Resize for compatibility
        print(f"Image loaded and resized successfully: {init_image.size}")


        # Generate the image using the pipeline
        try:
            output = img2img_pipe(
                prompt=prompt,
                image=init_image,
                strength=strength,
                guidance_scale=guidance_scale,
            )
            generated_image = output.images[0]
            print("Image generated successfully!")
        except Exception as e:
            print(f"Error during pipeline execution: {e}")
            return jsonify({"error": f"Image generation failed: {e}"}), 500

        # Save the generated image
        output_path = os.path.join(RESULTS_FOLDER, "generated_image.png")
        generated_image.save(output_path)
        return send_file(output_path, mimetype='image/png')

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({"error": "An unexpected error occurred"}), 500

@app.route('/test', methods=['GET'])
def test_pipeline():
    global img2img_pipe
    if img2img_pipe is None:
        return jsonify({"error": "Pipeline is not initialized yet. Try again later."}), 500

    try:
        test_image_path = os.path.join(UPLOAD_FOLDER, "input_image.png")
        print("Using a mock image for testing.")

        init_image = Image.open(test_image_path).convert("RGB")
        init_image = init_image.resize((512, 512))
        print(f"Using test image from uploads folder: {test_image_path}")

        # Generate a test image
        output = img2img_pipe(
            prompt="A timber modern residential house, large glazings",
            image=init_image,
            strength=0.75,
            guidance_scale=7.5,
        )
        generated_image = output.images[0]

        # Save the generated test image
        output_path = os.path.join(RESULTS_FOLDER, "test_output.png")
        generated_image.save(output_path)
        print(f"Generated test image saved at: {output_path}")

        return send_file(output_path, mimetype='image/png')
    except Exception as e:
        print(f"Error during test generation: {e}")
        return jsonify({"error": f"Test generation failed: {e}"}), 500

if __name__ == "__main__":
    app.run(debug=True)
