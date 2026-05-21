import streamlit as st
from encrypt import encrypt_image
from decrypt import decrypt_image
import os
import base64
import tempfile
import json # Import json for potential future use or clarity, though already used in encrypt/decrypt

# Set page config with animations
st.set_page_config(
    page_title="🔒 SecurePixel | Advanced Image Encryption",
    page_icon="🔐",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom styling
def set_app_style():
    st.markdown(
        """
        <style>
        /* Main app background */
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1639762681057-408e52192e55");
            background-size: cover;
            background-position: center;
            background-attachment: fixed;
        }
        
        /* Main container */
        .main-box {
            background-color: rgba(15, 15, 15, 0.92);
            border-radius: 15px;
            padding: 2.5rem;
            margin: 2rem auto;
            width: 80%;
            max-width: 800px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
            backdrop-filter: blur(7px);
            border: 1px solid rgba(254, 254, 254, 0.2);
        }
        
        /* Header styling */
        .main-header {
            font-size: 2.8rem;
            text-align: center;
            margin-bottom: 0.5rem;
            font-weight: 800;
            background: linear-gradient(45deg, #8a2be2, #9370db);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        
        /* File uploader styling */
        .stFileUploader > div > div {
            border: 2px dashed #7a4bcf !important;
            border-radius: 12px !important;
            padding: 25px !important;
            background-color: rgba(255, 255, 255, 0.12) !important;
        }
        
        /* Button styling */
        .stButton > button {
            background: linear-gradient(45deg, #6e48aa, #9d50bb);
            color: white !important;
            border: none;
            padding: 0.8rem 2rem;
            border-radius: 50px;
            font-weight: bold;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
            margin: 0.5rem 0;
            width: 100%;
            max-width: 250px;
        }
        
        /* Button hover effect */
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 7px 20px rgba(0,0,0,0.4);
        }
        
        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
            justify-content: center;
        }
        
        .stTabs [data-baseweb="tab"] {
            height: 50px;
            padding: 0 25px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 10px 10px 0 0 !important;
            border: none !important;
            font-weight: 600;
            color: #d1d1d1 !important;
        }

        /* Custom success/error messages */
        .stAlert {
            border-radius: 10px;
            padding: 15px 20px;
            font-size: 1.1rem;
            font-weight: 500;
        }
        .stAlert.success {
            background-color: rgba(40, 167, 69, 0.2); /* Greenish */
            color: #28a745;
            border-left: 5px solid #28a745;
        }
        .stAlert.error {
            background-color: rgba(220, 53, 69, 0.2); /* Reddish */
            color: #dc3545;
            border-left: 5px solid #dc3545;
        }
        .stAlert.warning {
            background-color: rgba(255, 193, 7, 0.2); /* Yellowish */
            color: #ffc107;
            border-left: 5px solid #ffc107;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

set_app_style()

# Main app container
st.markdown("""
<div class="main-box">
    <h1 class="main-header">SecurePixel</h1>
    <h1 class="main-header">(Image Encryption & Decryption)</h1>
    <p style="text-align:center;color:#e6e6e6;font-size:1.2rem;margin-bottom:2rem;">
        Military-grade image encryption with quantum-resistant algorithms
        <span style="font-size:0.9rem; cursor:pointer;" title="Uses AES-256 in EAX mode with PBKDF2 for key derivation, providing strong security against modern attacks. 'Quantum-resistant' refers to the use of robust, well-established algorithms that are not currently known to be vulnerable to quantum computing attacks.">ⓘ</span>
    </p>
""", unsafe_allow_html=True)

# Tabs for encryption/decryption
tab1, tab2 = st.tabs(["🔒 Encrypt Image", "🔓 Decrypt Image"])

with tab1:
    st.markdown("<h3 style='text-align:center;color:#e6e6e6;'>Protect Your Visual Secrets</h3>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "**Upload your sensitive image here:**",
        type=["png", "jpg", "jpeg", "webp", "bmp"],
        help="Only image files (PNG, JPG, JPEG, WEBP, BMP) up to 200MB are supported for encryption."
    )
    
    if uploaded_file:
        st.image(uploaded_file, caption="Original Image Preview", use_column_width=True)
    
    col1, col2 = st.columns(2)
    with col1:
        password = st.text_input("Encryption password", type="password", key="enc_pass")
        if password:
            # Simple password strength indicator
            strength = "Weak"
            color = "red"
            if len(password) >= 8:
                strength = "Medium"
                color = "orange"
            if any(char.isdigit() for char in password) and any(char.isupper() for char in password) and len(password) >= 12:
                strength = "Strong"
                color = "green"
            st.markdown(f"<p style='color:{color}; font-size:0.9rem; margin-top:-10px;'>Password Strength: <strong>{strength}</strong></p>", unsafe_allow_html=True)

    with col2:
        confirm_password = st.text_input("Confirm password", type="password", key="conf_pass")
    
    if st.button("🚀 Encrypt Now", key="enc_btn"):
        if not uploaded_file:
            st.error("❌ Please upload an image first.")
        elif not password or not confirm_password:
            st.error("⚠️ Please enter and confirm your password.")
        elif password != confirm_password:
            st.error("❌ Passwords do not match. Please re-enter.")
        elif len(password) < 8:
            st.error("⚠️ Password must be at least 8 characters long.")
        else:
            with st.spinner("Encrypting pixels with military-grade precision..."):
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(uploaded_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    encrypted_path = encrypt_image(tmp_path, password, "encrypted.bin")
                    
                    with open(encrypted_path, "rb") as f:
                        data = f.read()
                        b64 = base64.b64encode(data).decode()
                        href = f'<a href="data:application/octet-stream;base64,{b64}" download="secure_encrypted.bin" style="background: linear-gradient(45deg, #6e48aa, #9d50bb); color: white; padding: 0.8rem 2rem; border-radius: 50px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 1rem;">⬇️ Download Encrypted Image (secure_encrypted.bin)</a>'
                        st.success("✅ Encryption successful! Your image is now secure.")
                        st.balloons()
                        st.markdown(href, unsafe_allow_html=True)
                    
                    os.unlink(tmp_path)
                    os.unlink(encrypted_path)
                except Exception as e:
                    st.error(f"❌ Encryption failed: {str(e)}")
                    if 'tmp_path' in locals() and os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    if 'encrypted_path' in locals() and os.path.exists(encrypted_path):
                        os.unlink(encrypted_path)


with tab2:
    st.markdown("<h3 style='text-align:center;color:#e6e6e6;'>Restore Your Protected Images</h3>", unsafe_allow_html=True)
    
    encrypted_file = st.file_uploader(
        "**Upload your encrypted SecurePixel file (.bin):**",
        type=["bin"],
        help="This must be a .bin file previously encrypted using SecurePixel."
    )
    
    password = st.text_input("Decryption password", type="password", key="dec_pass")
    
    if st.button("🔓 Decrypt Now", key="dec_btn"):
        if not encrypted_file:
            st.error("❌ Please upload an encrypted file.")
        elif not password:
            st.error("⚠️ Password is required for decryption.")
        elif len(password) < 4:
            st.error("⚠️ Password must be at least 4 characters long.")
        else:
            with st.spinner("Unlocking your image, pixel by pixel..."):
                tmp_path = None # Initialize tmp_path
                decrypted_path = None # Initialize decrypted_path
                try:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
                        tmp_file.write(encrypted_file.getvalue())
                        tmp_path = tmp_file.name
                    
                    decrypted_path = decrypt_image(tmp_path, password)
                    
                    # To get the original format for download link, we need to re-read metadata
                    # This is a slight redundancy but ensures the correct format for download
                    # Alternatively, decrypt_image could return the shape_info
                    with open(tmp_path, "rb") as f_read_meta:
                        f_read_meta.read(16) # salt
                        f_read_meta.read(16) # nonce
                        f_read_meta.read(16) # tag
                        shape_len = int.from_bytes(f_read_meta.read(2), 'big')
                        shape_bytes = f_read_meta.read(shape_len)
                        shape_info = json.loads(shape_bytes.decode('utf-8'))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.image(decrypted_path, caption="Decrypted Image", use_column_width=True)
                    with col2:
                        with open(decrypted_path, "rb") as f:
                            data = f.read()
                            b64 = base64.b64encode(data).decode()
                            # Dynamically set data type and filename based on original format
                            mime_type = f"image/{shape_info['format']}" if shape_info['format'] != 'jpg' else 'image/jpeg' # Handle jpg vs jpeg
                            href = f'<a href="data:{mime_type};base64,{b64}" download="decrypted_image.{shape_info["format"]}" style="background: linear-gradient(45deg, #6e48aa, #9d50bb); color: white; padding: 0.8rem 2rem; border-radius: 50px; text-decoration: none; font-weight: bold; display: inline-block; margin-top: 1rem;">⬇️ Download Decrypted Image</a>'
                            st.success("🎉 Decryption successful! Your image is restored.")
                            st.balloons()
                            st.markdown(href, unsafe_allow_html=True)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "MAC check failed" in error_msg:
                        st.error("🚫 Incorrect password. Please try again.")
                    elif "Invalid file format" in error_msg or "not enough data" in error_msg or "Expecting value" in error_msg:
                        st.error("⚠️ Invalid encrypted file. Please upload a valid SecurePixel file.")
                    else:
                        st.error(f"❌ Decryption failed: {error_msg}")
                finally:
                    # Ensure temporary files are cleaned up
                    if tmp_path and os.path.exists(tmp_path):
                        os.unlink(tmp_path)
                    if decrypted_path and os.path.exists(decrypted_path):
                        os.unlink(decrypted_path)

# Footer
st.markdown("""
<div style='text-align: center; margin-top: 2rem; color: #aaaaaarii7;'>
    Built with ❤️ using Streamlit | AES-256 Encryption | SecurePixel v1.0
</div>
</div>
""", unsafe_allow_html=True)
