import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import pandas as pd
from io import BytesIO
import zipfile

# Function to generate certificates
def generate_certificate(template, names, font_path, font_size, color, x_position, y_position):
    font = ImageFont.truetype(font_path, font_size)
    certificates = []

    for name in names:
        certificate = template.copy()
        draw = ImageDraw.Draw(certificate)
        text_bbox = draw.textbbox((0, 0), name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_position = (x_position - text_width / 2, y_position - text_height / 2)
        draw.text(text_position, name, font=font, fill=color)
        certificates.append((name, certificate))

    return certificates

# Function to create a zip file of certificates
def create_zip(certificates):
    buffer = BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for name, certificate in certificates:
            img_buffer = BytesIO()
            certificate.save(img_buffer, format="JPEG")
            img_buffer.seek(0)
            zf.writestr(f"{name}_certificate.jpg", img_buffer.read())
    buffer.seek(0)
    return buffer

# Function for the Home page
def home():
    st.header("🎉 Welcome to the CertiGen Web App! 🎉")
    st.write("This web app allows you to easily generate certificates for your events or courses on ur given names. Here's how it works:")
    
    # Informative sections
    st.markdown("### 🌟 Key Features:")
    st.write("1. **Upload a Certificate Template**: Start by uploading a background template for your certificates.")
    st.image("sample_certificate.png", use_column_width=True)
    
    st.write("2. **Customize Text Style**: Choose the font, size, and color to match your theme.")
    st.image("2.png", use_column_width=True)
    
    st.write("3. **Add Names from a File**: Easily upload a CSV file with the names of your participants.")
    st.image("3.png", use_column_width=True)
    
    st.write("4. **Preview and Generate**: Preview the certificates and generate them with a single click.")
    st.image("4.png", use_column_width=True)
    
    st.write("5. **Download Certificates**: Get all the generated certificates in a zip file.")
    st.image("5.png", use_column_width=True)

    # Highlight Benefits
    st.markdown("### 🎁 Benefits:")
    st.write("✅ **Time-Saving**: Generate multiple certificates at once.")
    st.write("✅ **Customizable**: Tailor the look and feel to your needs.")
    st.write("✅ **User-Friendly**: Easy-to-use interface for everyone.")
    

    # Final Touch
    st.markdown("### 🚀 Ready to Get Started?")
    st.write("Navigate to the **Certificate Generator** page from the sidebar to begin!")
    st.balloons()

# Function for the About page
def about():
    st.title("About")
    st.header("About the Developer")
    st.write("👨‍💻 This web app was developed by **Gashahun Woldeyohannes**.")
    st.write("🚀 Gashahun is a passionate developer with expertise in web development and data science.")
    
    # Developer image
    st.image("https://via.placeholder.com/400x400.png?text=Developer+Image", use_column_width=True)
    
    st.markdown("### Connect with me:")
    col1 = st.columns(1)
    with col1:
        st.markdown("[![LinkedIn](https://img.shields.io/badge/LinkedIn-blue?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/gashahun-woldeyohannes)")

    # Additional information
    st.markdown("### More About Me:")
    st.write("🌟 I love creating web apps, exploring new technologies, and sharing knowledge with the community.")
    st.write("📚 Currently, I'm delving deeper into machine learning and artificial intelligence.")
    st.write("🎨 In my free time, I enjoy graphic design and creating digital art.")
    
    # Fun elements
    st.balloons()

# Function for the Certificate Generator page
def certificate_generator():
    st.title("Certificate Generator")
    template_file = st.file_uploader("Upload Certificate Template", type=["jpg", "png"])
    if template_file:
        template = Image.open(template_file)
        font_file = st.file_uploader("Upload Font File", type=["ttf", "otf"])
        if font_file:
            font_path = font_file.name
            with open(font_path, "wb") as f:
                f.write(font_file.getbuffer())
            font_size = st.number_input("Font Size", min_value=10, max_value=300, value=100)
            color = st.color_picker("Text Color", "#000000")
            color = tuple(int(color.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
            names_file = st.file_uploader("Upload Names File (CSV)", type=["csv"])
            if names_file:
                try:
                    df = pd.read_csv(names_file)
                    names = df.iloc[:, 0].tolist()
                    y_position = st.slider("Y Position", min_value=0, max_value=template.height, value=int(template.height / 2))
                    x_position = st.slider("X Position", min_value=0, max_value=template.width, value=int(template.width / 2))
                    st.subheader("Preview Certificate")
                    preview_name = st.selectbox("Select Name for Preview", names)
                    preview_certificate = generate_certificate(template, [preview_name], font_path, font_size, color, x_position, y_position)[0][1]
                    st.image(preview_certificate)
                    if st.button("Generate Certificates"):
                        certificates = generate_certificate(template, names, font_path, font_size, color, x_position, y_position)
                        progress_bar = st.progress(0)
                        for i, (name, _) in enumerate(certificates):
                            progress_bar.progress((i + 1) / len(certificates))
                        zip_buffer = create_zip(certificates)
                        st.success("Certificates generated successfully!")
                        st.download_button(label="Download Certificates", data=zip_buffer, file_name="certificates.zip", mime="application/zip")
                except Exception as e:
                    st.error(f"Error reading file: {e}")

# Main function to control the navigation
def main():
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox("Go to", ["Home", "About", "Certificate Generator"], index=2)  # Default to "Certificate Generator"

    if page == "Home":
        home()
    elif page == "About":
        about()
    elif page == "Certificate Generator":
        certificate_generator()

if __name__ == "__main__":
    main()
