import json

def convert_to_json(file_path):
    videos = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for i in range(0, len(lines), 3):
            video = {
                'name': lines[i].strip(),
                'thumbnail_url': lines[i+1].strip(),
                'url': lines[i+2].strip()
            }
            videos.append(video)
    return videos

def save_as_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)

def main():
    input_file_path = 'd_text.txt'
    output_file_path = 'converted_file.txt'

    videos = convert_to_json(input_file_path)
    save_as_json(output_file_path, videos)

    print(f"Conversion completed. Data saved to {output_file_path}")

if __name__ == "__main__":
    main()
