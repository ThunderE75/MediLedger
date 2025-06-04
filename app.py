import streamlit as st
import hashlib
import json
import os
from datetime import datetime
import pytesseract
from PIL import Image
import io

# Simulated Blockchain and Off-Chain Storage
BLOCKCHAIN_FILE = "blockchain.json"
STORAGE_FOLDER = "documents"
os.makedirs(STORAGE_FOLDER, exist_ok=True)

# ------------------- Helper Functions -------------------
def load_blockchain():
    if not os.path.exists(BLOCKCHAIN_FILE):
        return []
    with open(BLOCKCHAIN_FILE, 'r') as f:
        return json.load(f)

def save_blockchain(chain):
    with open(BLOCKCHAIN_FILE, 'w') as f:
        json.dump(chain, f, indent=4)

def compute_hash(file_bytes):
    return hashlib.sha256(file_bytes).hexdigest()

def classify_document(file_bytes):
    try:
        image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
        text = pytesseract.image_to_string(image).lower()

        if "x-ray" in text or "radiograph" in text:
            return "X-ray Report"
        elif "hemoglobin" in text or "cbc" in text or "platelet" in text:
            return "Blood Test Report"
        elif "mri" in text:
            return "MRI Scan Report"
        elif "urine" in text:
            return "Urine Test Report"
        else:
            return "General Medical Document"
    except Exception:
        return "Unknown"

def create_block(file_hash, uploader, access_list, doc_type):
    chain = load_blockchain()
    previous_hash = chain[-1]['block_hash'] if chain else '0'
    block = {
        'timestamp': str(datetime.now(datetime.UTC)),
        'file_hash': file_hash,
        'uploader': uploader,
        'access_list': access_list,
        'document_type': doc_type,
        'previous_hash': previous_hash
    }
    block['block_hash'] = compute_hash(json.dumps(block).encode())
    chain.append(block)
    save_blockchain(chain)
    return block

def verify_access(user, file_hash):
    for block in load_blockchain():
        if block['file_hash'] == file_hash and user in block['access_list']:
            return True
    return False

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="Blockchain Health Storage", page_icon="📄", layout="wide")

with st.container():
    col1, col2 = st.columns([10, 1])
    with col2:
        st.markdown("""
            <a href="https://drive.google.com/file/d/1c1A8jm0z-Pj0hpBFGh_82oUslqZXvbvv/view?usp=drive_link" target="_blank">
                <button title="View Research Paper">📄 Research Paper</button>
            </a>
        """, unsafe_allow_html=True)

st.title("MediLedger")

st.markdown("""
**MediLedger** is a proof-of-concept application demonstrating secure storage and permission-based access to healthcare documents using blockchain technology. 
This system is part of a research effort exploring decentralized architectures for medical data handling. A detailed explanation of the proposed framework and implementation is available in the accompanying research paper.
""")

st.sidebar.title("User Panel")
role = st.sidebar.radio("Select Role", ["Patient", "Provider"])
user_id = st.sidebar.text_input("Enter Your User ID")

if role == "Patient":
    st.header("Upload Healthcare Document")
    uploaded_file = st.file_uploader("Choose a JPG, PNG, or TIFF file", type=['jpg', 'jpeg', 'png', 'tiff'])
    if uploaded_file:
        access_input = st.text_input("Enter comma-separated provider IDs to grant access")
        if st.button("Upload and Register on Blockchain"):
            file_bytes = uploaded_file.read()
            file_hash = compute_hash(file_bytes)
            file_path = os.path.join(STORAGE_FOLDER, file_hash)
            with open(file_path, 'wb') as f:
                f.write(file_bytes)
            access_list = [x.strip() for x in access_input.split(",") if x.strip()]
            doc_type = classify_document(file_bytes)
            block = create_block(file_hash, user_id, access_list, doc_type)
            st.success("Document successfully registered!")
            st.json(block)

elif role == "Provider":
    st.header("Request Document Access")
    file_hash_input = st.text_input("Enter File Hash")
    if st.button("Request Access"):
        if verify_access(user_id, file_hash_input):
            file_path = os.path.join(STORAGE_FOLDER, file_hash_input)
            if os.path.exists(file_path):
                with open(file_path, 'rb') as f:
                    st.download_button("Download Document", f.read(), file_hash_input + ".pdf")
            else:
                st.error("File not found in storage.")
        else:
            st.error("Access Denied: You are not authorized to view this document.")

st.sidebar.markdown("---")
if st.sidebar.button("View Blockchain"):
    st.sidebar.subheader("Blockchain Ledger")
    chain = load_blockchain()
    for i, block in enumerate(chain):
        st.sidebar.markdown(f"**Block {i+1}:**")
        st.sidebar.json(block)
