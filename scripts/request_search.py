from pathlib import Path

import requests

from config import read_configuration, get_service_url


def main():
    file_path = Path(__file__).parent / "data" / "test" / "face_3.jpg"

    # Read configuration file.
    configuration = read_configuration()
    if configuration:
        url = get_service_url(configuration, "search?limit=2")

        with open(file_path.resolve(), "rb") as file:
            files_to_search = {"file": (file_path.name, file, "image/jpeg"), }
            data = {"limit": 2, }

            response = requests.post(url, files=files_to_search, data=data)

            if response.status_code == 200:
                print(f"Успешно")
                print(response.json())
            else:
                print(f"Ошибка: {response.status_code}, {response.text}")


if __name__ == "__main__":
    main()
