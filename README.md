# MediLedger: An app to store Healthcare documents on Blockchain

MediLedger is a proof-of-concept application that demonstrates secure, permission-based storage and retrieval of healthcare documents using blockchain technology. It simulates decentralized access control, immutable logging, and document integrity verification through a custom-built blockchain implemented in Python. A detailed explanation of the system's architecture, design rationale, and implementation is provided in the accompanying [research paper](https://drive.google.com/file/d/1c1A8jm0z-Pj0hpBFGh_82oUslqZXvbvv/view?usp=drive_link).

## Installation

> Running locally on Ubuntu/Debian based distribution

1. Clone the repository

    ```
    git clone https://github.com/ThunderE75/MediLedger MediLedger
    ```
1. Install dependencies 

    - Python 3.11
    - pip
    - venv
    - streamlit

    ```
    sudo apt install python3-pip venv
    ```
1. Navigate to the project repository

    ```
    cd MediLedger
    ```
1. Setup and activate a python virtual environment. *(optional but recommended)*
    
    ```
    python3 -m venv MediLedger
    MediLedger\bin\activate
    ```
    ```
    python -m venv MediLedger
    MediLedger\Scripts\activate.bat
    ```
2. Install all the required packages from `requirements.txt`

    ```
    pip3 install -r requirements.txt
    ```