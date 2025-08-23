import requests

from config import read_configuration, get_service_url


def main():
    # Read configuration file.
    configuration = read_configuration()
    if configuration:
        url = get_service_url(configuration, "embed_status")
        response = requests.get(url)

        if response.status_code == 200:
            print(f"Успешно")
            print(response.json())
        else:
            print(f"Ошибка: {response.status_code}, {response.text}")


if __name__ == "__main__":
    main()
