from flask import Flask, render_template, request
from PIL import Image
from scipy import stats

app = Flask(__name__)

def analyze_lsb(image_path):
  """
  Analyzes the least significant bit (LSB) of each pixel in an image 
  and performs basic statistical tests.

  Args:
      image_path (str): Path to the image file.

  Returns:
      dict: Dictionary containing analysis results.
  """
  try:
    # Open the image
    img = Image.open(image_path)

    # Convert to RGB mode if needed (LSB analysis works on RGB values)
    if img.mode != 'RGB':
        img = img.convert("RGB")
    width, height = img.size

    # Analyze each pixel
    lsb_values = []
    for x in range(width):
      for y in range(height):
        r, g, b = img.getpixel((x, y))
        # Extract least significant bit from each color channel
        lsb_values.append(r & 1)
        lsb_values.append(g & 1)
        lsb_values.append(b & 1)

    # Analyze LSB distribution
    one_count = lsb_values.count(1)
    zero_count = len(lsb_values) - one_count
    total_bits = len(lsb_values)

    # Chi-square test for randomness
    expected_ones = total_bits / 2
    chi2, pval = stats.chisquare([one_count, zero_count])

    # Prepare results dictionary
    results = {
        "image": image_path,
        "ones_count": one_count,
        "zeros_count": zero_count,
        "expected_ones": expected_ones,
        "chi2": chi2,
        "pval": pval,
    }

    return results

  except FileNotFoundError:
    return {"error": "Image file not found"}

@app.route("/", methods=["GET", "POST"])
def index():
  if request.method == "POST":
    uploaded_file = request.files.get("image_file")
    if uploaded_file:
      # Save the uploaded image (implement security measures for real applications)
      image_path = "F:\crypto\Crypt\imagesdd.jpg"
      uploaded_file.save(image_path)
      # Perform analysis
      analysis_results = analyze_lsb(image_path)
      return render_template("index.html", results=analysis_results)
    else:
      return render_template("index.html", results=None)

if __name__ == "__main__":
  app.run(debug=True)
