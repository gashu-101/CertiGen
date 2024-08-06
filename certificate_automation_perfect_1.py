import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from io import BytesIO
import zipfile
import os

def generate_certificate(template, names, font_path, font_size, color, y_position):
    # Load the font
    font = ImageFont.truetype(font_path, font_size)
    certificates = []

    for name in names:
        # Create a copy of the template for each name
        certificate = template.copy()
        draw = ImageDraw.Draw(certificate)
        # Calculate the bounding box of the text to be added
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        
        # Calculate the position to center the text horizontally and place it at the specified y position
        pos_x = template.width / 2
        pos_y = y_position
        
        # Calculate the position to place the text
        text_position = (pos_x - text_width / 2, pos_y - text_height / 2)
        
        # Add the name to the certificate
        draw.text(text_position, name, font=font, fill=color)
        
        # Add to list
        certificates.append((name, certificate))

    return certificates

def create_zip(certificates):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, certificate in certificates:
            # Save the certificate to a bytes buffer
            img_buffer = BytesIO()
            certificate.save(img_buffer, format="JPEG")
            img_buffer.seek(0)
            # Add the image to the zip file
            zf.writestr(f"{name}_certificate.jpg", img_buffer.read())
    buffer.seek(0)
    return buffer

def main():
    st.title("Certificate Generator")

    # Upload certificate template
    template_file = st.file_uploader("Upload Certificate Template", type=["jpg", "png"])
    if template_file:
        template = Image.open(template_file)

        # Upload font file
        font_file = st.file_uploader("Upload Font File", type=["ttf", "otf"])
        if font_file:
            font_path = font_file.name
            with open(font_path, "wb") as f:
                f.write(font_file.getbuffer())
            
            # Font size input
            font_size = st.number_input("Font Size", min_value=10, max_value=300, value=100)
            
            # Color picker
            color = st.color_picker("Text Color", "#000000")
            color = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

            # Upload names file
            names_file = st.file_uploader("Upload Names File (CSV/Excel)", type=["csv", "xlsx"])
            if names_file:
                try:
                    if names_file.name.endswith(".csv"):
                        df = pd.read_csv(names_file)
                    else:
                        df = pd.read_excel(names_file)
                    
                    names = df.iloc[:, 0].tolist()
                    
                    # Y position slider
                    y_position = st.slider("Y Position", min_value=0, max_value=template.height, value=int(template.height / 2))

                    # Preview certificate
                    st.subheader("Preview Certificate")
                    preview_name = st.selectbox("Select Name for Preview", names)
                    preview_certificate = generate_certificate(template, [preview_name], font_path, font_size, color, y_position)[0][1]
                    st.image(preview_certificate)

                    # Generate certificates button
                    if st.button("Generate Certificates"):
                        certificates = generate_certificate(template, names, font_path, font_size, color, y_position)
                        
                        # Show progress
                        progress_bar = st.progress(0)
                        for i, (name, _) in enumerate(certificates):
                            progress_bar.progress((i + 1) / len(certificates))

                        # Create zip file
                        zip_buffer = create_zip(certificates)
                        
                        st.success("Certificates generated successfully!")
                        st.download_button(
                            label="Download Certificates",
                            data=zip_buffer,
                            file_name="certificates.zip",
                            mime="application/zip"
                        )
                except Exception as e:
                    st.error(f"Error reading file: {e}")

if __name__ == "__main__":
    main()
