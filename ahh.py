import os
from cryptography.fernet import Fernet

def encrypt_text(text, key):
    f = Fernet(key)
    encrypted_text = f.encrypt(text.encode('utf-8'))
    return encrypted_text

def main():
    # Get key from environment variables
    key = os.getenv("ENCRYPTION_KEY")
    if key is None:
        print("Encryption key not found in environment variables.")
        return

    # Input and output file paths
    input_file_path = "converted.txt"
    output_file_path = "xdd.txt"

    # Read text from file
    with open(input_file_path, "r") as f:
        text = f.read()

    # Encrypt the text
    encrypted_text = encrypt_text(text, key)

    # Write encrypted text to a new file
    with open(output_file_path, "wb") as f:
        f.write(encrypted_text)

    print("Encryption completed. Encrypted text written to:", output_file_path)

if __name__ == "__main__":
    main()
