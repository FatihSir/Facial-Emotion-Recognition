import React, { useState } from "react";
import "./App.css"; // External CSS for styling

function App() {
  const [imagePreview, setImagePreview] = useState(null);
  const [uploadedImage, setUploadedImage] = useState(null);
  const [prediction, setPrediction] = useState(null);
  const [gradcamImage, setGradcamImage] = useState(null);

  // Handle file upload and preview
  const handleFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      const reader = new FileReader();
      reader.onload = (e) => {
        setImagePreview(e.target.result);
      };
      reader.readAsDataURL(file);
    }
  };

  // Handle form submission
  const handleFormSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    try {
      const response = await fetch("/", {
        method: "POST",
        body: formData,
      });
      const data = await response.json();
      setUploadedImage(data.image_url);
      setPrediction(data.prediction);
      setGradcamImage(data.gradcam_url);
    } catch (error) {
      console.error("Error:", error);
    }
  };

  return (
    <div className="container">
      {/* Logo */}
      <img
        src="/static/omu.png"
        alt="Ondokuz Mayis University Logo"
        className="logo"
      />

      {/* Title and Description */}
      <h1>Cat & Dog Classifier</h1>
      <p className="description">
        Upload an image to classify whether it features a cat or a dog. Our AI
        model will also generate a Grad-CAM heatmap for visualization.
      </p>

      {/* Form */}
      <form className="form-group" onSubmit={handleFormSubmit}>
        <input
          className="form-control"
          type="file"
          name="imagefile"
          id="imagefile"
          accept="image/*"
          onChange={handleFileChange}
          required
        />
        <button className="btn" type="submit">
          Predict Image
        </button>
      </form>

      {/* Preview */}
      {imagePreview && (
        <div className="preview">
          <h2>Image Preview</h2>
          <img src={imagePreview} alt="Image Preview" />
        </div>
      )}

      {/* Uploaded Image */}
      {uploadedImage && (
        <div className="preview">
          <h2>Uploaded Image</h2>
          <img src={uploadedImage} alt="Uploaded Image" />
        </div>
      )}

      {/* Grad-CAM Heatmap */}
      {gradcamImage && (
        <div className="heatmap">
          <h2>Grad-CAM Visualization</h2>
          <img src={gradcamImage} alt="Grad-CAM Heatmap" />
        </div>
      )}

      {/* Prediction Result */}
      {prediction && <p className="result">{prediction}</p>}

      {/* Footer */}
      <div className="footer">
        Developed by{" "}
        <a href="https://github.com/FatihSir" target="_blank" rel="noreferrer">
          MOHAMEDALFATEH T. M. SAEED
        </a>
      </div>
    </div>
  );
}

export default App;