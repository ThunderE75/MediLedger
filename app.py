import streamlit as st
import hashlib
import json
import os
from datetime import datetime, timezone
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

def create_block(file_hash, uploader, access_list, doc_type, remarks):
    chain = load_blockchain()
    previous_hash = chain[-1]['block_hash'] if chain else '0'
    block = {
        'timestamp': str(datetime.now(timezone.utc)),
        'file_hash': file_hash,
        'uploader': uploader,
        'access_list': access_list,
        'document_type': doc_type,
        'remarks': remarks,
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

def get_user_documents(user):
    docs = []
    for block in load_blockchain():
        if block['uploader'] == user or user in block['access_list']:
            docs.append(block)
    return docs

# ------------------- Streamlit UI -------------------
st.set_page_config(page_title="Blockchain Health Storage", page_icon="📄", layout="wide")
# Header UI
st.markdown("""
    <div style='text-align: center; padding: 20px; background: linear-gradient(to left, #fc4e42, #fc8c42); border-radius: 0px;'>
        <h1 style='color: white;'>MediLedger</h1>
        <p style='color: white; font-size: 18px;'> An app to store Healthcare documents on Blockchain</p>
    </div>
""", unsafe_allow_html=True)

# s

st.sidebar.title("Login")

st.sidebar.markdown("""
<div style='text-align: left; padding: 0px'>
    <a href="https://drive.google.com/file/d/1c1A8jm0z-Pj0hpBFGh_82oUslqZXvbvv/view?usp=drive_link" target="_blank">
    <button title="View Research Paper">📄 View Research Paper</button>
</a>
</div>
""", unsafe_allow_html=True)

login_tab, provider_tab, view_chain_tab = st.sidebar.tabs(["User Login", "Provider Login", "View Blockchain"])


with login_tab:
    user_username = st.text_input("Username", key="user_username")
    user_password = st.text_input("Password", type="password", key="user_password")
    col1, col2 = st.columns([1, 1])
    if col1.button("Login as User"):
        st.session_state['logged_in'] = True
        st.session_state['user_type'] = "User"
        st.session_state['username'] = user_username
    if col2.button("Logout", key="logout_user"):
        st.session_state.clear()
        st.rerun()


with provider_tab:
    provider_username = st.text_input("Username", key="provider_username")
    provider_password = st.text_input("Password", type="password", key="provider_password")
    col1, col2 = st.columns([1, 1])
    if col1.button("Login as Provider"):
        st.session_state['logged_in'] = True
        st.session_state['user_type'] = "Healthcare Provider"
        st.session_state['username'] = provider_username
    if col2.button("Logout", key="logout_provider"):
        st.session_state.clear()
        st.rerun()
        
with view_chain_tab:
    st.subheader("Blockchain Ledger")
    chain = load_blockchain()
    if chain:
        for i, block in enumerate(chain):
            st.markdown(f"**Block {i+1}:**")
            st.json(block)
    else:
        st.info("Blockchain is currently empty.")


if st.session_state.get('logged_in'):
    user_type = st.session_state['user_type']
    username = st.session_state['username']
    st.sidebar.success(f"Logged in as {user_type}: {username}")
    if user_type == "User":
        st.header("Your Documents")
        user_docs = get_user_documents(username)
        if user_docs:
            cols = st.columns(3)
            for i, block in enumerate(user_docs):
                file_path = os.path.join(STORAGE_FOLDER, block['file_hash'])
                try:
                    with open(file_path, 'rb') as f:
                        image_bytes = f.read()
                    with cols[i % 3]:
                        st.image(image_bytes, caption=block['document_type'], use_container_width=True)
                        with st.expander("View Metadata"):
                            st.json(block)
                except Exception:
                    st.warning(f"Document {i+1} could not be loaded.")
        else:
            st.info("No documents found for your account.")

    elif user_type == "Healthcare Provider":
        st.header("Upload Patient Document")
        patient_id = st.text_input("Patient Username")
        report_type = st.selectbox("Report Type", ["X-ray", "Blood Test", "Urine Test", "MRI Scan", "Other"])
        remarks = st.text_area("Remarks")
        uploaded_file = st.file_uploader("Upload Medical Document", type=['jpg', 'jpeg', 'png', 'tiff'])

        if uploaded_file:
            if st.button("Upload and Register on Blockchain"):
                file_bytes = uploaded_file.read()
                file_hash = compute_hash(file_bytes)
                file_path = os.path.join(STORAGE_FOLDER, file_hash)
                with open(file_path, 'wb') as f:
                    f.write(file_bytes)
                doc_type = report_type + " Report"
                access_list = [patient_id]
                block = create_block(file_hash, username, access_list, doc_type, remarks)
                st.success("Document successfully registered!")
                st.json(block)
