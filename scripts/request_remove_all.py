import requests

from config import read_configuration, get_service_url


def main():
    # Read configuration file.
    configuration = read_configuration()
    if configuration:
        url = get_service_url(configuration, "remove_all")
        response = requests.delete(url)

        if response.status_code == 200:
            print(f"Успешно")
        else:
            print(f"Ошибка: {response.status_code}, {response.text}")


if __name__ == "__main__":
    main()
