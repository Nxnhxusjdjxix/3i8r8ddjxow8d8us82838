import os
from cryptography.fernet import Fernet

def decrypt_text(encrypted_text, key):
    f = Fernet(key)
    decrypted_text = f.decrypt(encrypted_text)
    return decrypted_text.decode('utf-8')

def main():
    # Get key from environment variables
    key = os.getenv("ENCRYPTION_KEY")
    if key is None:
        print("Decryption key not found in environment variables.")
        return

    # Input and output file paths
    input_file_path = "videos.txt"
    output_file_path = "d_text.txt"

    # Read encrypted text from file
    with open(input_file_path, "rb") as f:
        encrypted_text = f.read()

    # Decrypt the text
    decrypted_text = decrypt_text(encrypted_text, key)

    # Write decrypted text to a new file
    with open(output_file_path, "w") as f:
        f.write(decrypted_text)

    print("Decryption completed. Decrypted text written to:", output_file_path)

if __name__ == "__main__":
    main()
