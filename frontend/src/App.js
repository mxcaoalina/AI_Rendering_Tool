import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [image, setImage] = useState(null);
  const [prompt, setPrompt] = useState('');
  const [preset, setPreset] = useState('Futuristic'); // Default preset
  const [generatedImage, setGeneratedImage] = useState(null);

  // Handle file upload
  const handleImageUpload = (event) => {
    setImage(event.target.files[0]);
  };

  // Handle image generation
  const handleGenerate = async () => {
    if (!prompt || !preset || !image) {
      alert('Please provide all inputs');
      return;
    }

    try {
      // Upload the image first
      if (image) {
        const formData = new FormData();
        formData.append('image', image);

        const uploadResponse = await axios.post('http://127.0.0.1:5000/upload', formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
        });
        console.log('Image uploaded successfully:', uploadResponse.data.file_path);
      }

      // Generate the rendering
      const formData = new FormData();
      formData.append('prompt', prompt);
      formData.append('preset', preset);

      if (image) {
        formData.append('image', image); // Include the image if required by `/generate`
      }
  
      const response = await axios.post('http://127.0.0.1:5000/generate', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        responseType: 'blob', // Expect binary data for the image
      });
  
      // Display the generated image
      const url = URL.createObjectURL(new Blob([response.data]));
      setGeneratedImage(url);
    } catch (error) {
      console.error('Error generating image:', error);
      alert('Failed to generate the image. Please check the console for details.');
    }
  };

  return (
    <div style={{ textAlign: 'center', marginTop: '50px' }}>
      <h1>AI Architectural Rendering Tool</h1>

      {/* File Upload */}
      <div>
        <input
          type="file"
          accept="image/*"
          onChange={handleImageUpload}
          style={{ margin: '20px 0' }}
        />
      </div>

      {/* Text Prompt */}
      <div>
        <textarea
          placeholder="Enter a prompt for rendering..."
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          rows={4}
          cols={50}
          style={{ margin: '20px 0' }}
        />
      </div>

      {/* Preset Dropdown */}
      <div>
        <label htmlFor="preset">Choose a preset:</label>
        <select
          id="preset"
          value={preset}
          onChange={(e) => setPreset(e.target.value)}
          style={{ margin: '10px'}}
          >
            <option value="Futuristic">Futuristic</option>
            <option value="Modern Minimalism">Modern Minimalism</option>
            <option value="Surrealism">Surrealism</option>
          </select>
      </div>

      {/* Generate Button */}
      <div>
        <button
          onClick={handleGenerate}
          style={{ padding: '10px 20px', fontSize: '16px' }}
        >
          Generate Rendering
        </button>
      </div>

      {/* Display Generated Image */}
      {generatedImage && (
        <div style={{ marginTop: '30px' }}>
          <h2>Generated Image:</h2>
          <img
            src={generatedImage}
            alt="Generated rendering"
            style={{ maxWidth: '80%', maxHeight: '400px' }}
          />
        </div>
      )}
    </div>
  );
}

export default App;
