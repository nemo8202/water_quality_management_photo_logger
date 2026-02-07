from PIL import Image

def convert():
    try:
        img = Image.open("favicon.png")
        img.save("favicon.ico", format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
        print("Successfully converted favicon.jpg to favicon.ico")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    convert()
