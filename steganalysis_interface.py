from PIL import Image
from scipy import stats

def analyze_lsb(image_path):
  """
  Analyzes the least significant bit (LSB) of each pixel in an image 
  and performs basic statistical tests.

  Args:
      image_path (str): Path to the image file.

  Returns:
      None: Prints analysis results to the console.
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

    # Print results
    print(f"Image: {image_path}")
    print(f"Number of 1s in LSBs: {one_count}")
    print(f"Number of 0s in LSBs: {zero_count}")
    print(f"Expected number of 1s: {expected_ones}")
    print(f"Chi-square statistic: {chi2:.4f}")
    print(f"p-value: {pval:.4f}")

    # Interpretation
    print("\nInterpretation:")
    if pval < 0.05:  # Adjust significance level as needed
        print("  - The distribution of 1s and 0s in LSBs significantly deviates from randomness, suggesting possible steganography.")
    else:
        print("  - The LSB distribution appears close to random, but further analysis might be needed.")

  except FileNotFoundError:
    print(f"Error: Image file not found: {image_path}")

def main():
  """
  Prompts user for image path and runs analysis.
  """
  while True:
    image_path = input("Enter the image path (or 'q' to quit): ")
    if image_path.lower() == 'q':
      break
    analyze_lsb(image_path)

if __name__ == "__main__":
  main()
