import os
import re
import shutil
import sys
import tempfile

"""
This script fixes the user guide HTML file by updating image paths to work correctly
in both development and PyInstaller packaged environments.
"""

def fix_user_guide():
    # Determine the base path for finding resources
    if getattr(sys, 'frozen', False):
        # Running from PyInstaller bundle
        base_path = sys._MEIPASS if hasattr(sys, '_MEIPASS') else os.path.dirname(sys.executable)
    else:
        # Running in development
        script_dir = os.path.dirname(os.path.abspath(__file__))
        base_path = script_dir  # TheAIReview directory
    
    print(f"Base path: {base_path}")
    
    # Find the user guide
    html_path = os.path.join(base_path, "docs", "user_guide.html")
    
    if not os.path.exists(html_path):
        print(f"Error: User guide not found at {html_path}")
        return False
    
    print(f"Found user guide at {html_path}")
    
    # Create a temp directory to hold a modified copy with corrected paths
    temp_dir = os.path.join(tempfile.gettempdir(), "AIReviewTool_docs")
    os.makedirs(temp_dir, exist_ok=True)
    
    # Create images directory structure in the temp folder
    temp_images = os.path.join(temp_dir, "images")
    temp_images_docs = os.path.join(temp_dir, "images", "docs")
    os.makedirs(temp_images, exist_ok=True)
    os.makedirs(temp_images_docs, exist_ok=True)
    
    print(f"Created temp directory: {temp_dir}")
    
    # Copy base images
    found_images = []
    for img_file in ["TR.png", "logo.png", "bot.JPG"]:
        src = os.path.join(base_path, "images", img_file)
        if os.path.exists(src):
            dest = os.path.join(temp_images, img_file)
            shutil.copy(src, dest)
            found_images.append((f"../images/{img_file}", f"images/{img_file}"))
            print(f"Copied image: {img_file}")
        else:
            print(f"Warning: Image file not found: {src}")
    
    # Copy doc images
    found_doc_images = []
    for img_file in ["AIR.png", "AIR_2.png", "Gt_1.png", "Gt_2.png", "Gt_3.png"]:
        src = os.path.join(base_path, "images", "docs", img_file)
        if os.path.exists(src):
            dest = os.path.join(temp_images_docs, img_file)
            shutil.copy(src, dest)
            found_doc_images.append((f"../images/docs/{img_file}", f"images/docs/{img_file}"))
            print(f"Copied doc image: {img_file}")
        else:
            print(f"Warning: Doc image file not found: {src}")
    
    # Read the original HTML content
    with open(html_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Replace the image paths in the HTML content
    fixed_html = html_content
    for old_path, new_path in found_images + found_doc_images:
        fixed_html = fixed_html.replace(old_path, new_path)
        print(f"Updated path: {old_path} -> {new_path}")
    
    # Also replace any url('../images/... references in CSS
    fixed_html = re.sub(r"url\(['\"]?\.\.\/images\/", r"url('images/", fixed_html)
    print("Updated CSS background image paths")
    
    # Write the modified HTML to the temp directory
    temp_guide_path = os.path.join(temp_dir, "user_guide.html")
    with open(temp_guide_path, 'w', encoding='utf-8') as f:
        f.write(fixed_html)
    
    print(f"Created modified user guide at: {temp_guide_path}")
    print(f"Open this file in your browser to view with correct images: {temp_guide_path}")
    
    return temp_guide_path

if __name__ == "__main__":
    fixed_path = fix_user_guide()
    if fixed_path:
        if sys.platform == 'win32':
            os.system(f'start "" "{fixed_path}"')
        else:
            import webbrowser
            webbrowser.open(f"file://{fixed_path}")
