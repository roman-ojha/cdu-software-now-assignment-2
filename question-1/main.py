def encrypt_text():
    """
    We will encrypt the text preset in raw_text.txt file by using double shift rules.
    Store the encrypted text into encrypted_text.txt file.
    Also store the shifts used for each character in shifts.txt file for decryption purpose.
    """

    # reading shifts from user input
    shift1 = int(input("Enter shift 1: "))
    shift2 = int(input("Enter shift 2: "))

    # reading raw text
    with open("raw_text.txt", "r", encoding="utf-8") as f:
        raw = f.read()

    encrypted = ""
    shifts = []
    for c in raw:
        if c.islower():
            s = shift1*shift2 if 'a' <= c <= 'm' else -(shift1+shift2)
        elif c.isupper():
            s = -shift1 if 'A' <= c <= 'M' else shift2**2
        else:
            s = 0
        encrypted += chr((ord(c) + s) % 256)
        shifts.append(s)

    # storing encrypted text
    with open("encrypted_text.txt", "w", encoding="utf-8") as f:
        f.write(encrypted)

    # storing shifts into shifts.txt
    with open("shifts.txt", "w", encoding="utf-8") as f:
        f.write(" ".join(map(str, shifts)))

    print("Successfully encrypted")


def decrypt_text():
    pass


def main():
    print("1) Encrypt Text: \n2) Decrypt Text: \n")
    encrypt = int(input("Enter option 1 or 2:"))

    if encrypt == 1:
        encrypt_text()
    elif encrypt == 2:
        decrypt_text()
    else:
        print("Invalid option selected.")


if __name__ == "__main__":
    main()
