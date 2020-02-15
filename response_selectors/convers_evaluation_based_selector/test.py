import requests
import json


def main():
    with open('test_data.json', 'r') as f:
        data = json.load(f)
    result = requests.post("http://localhost:8009/respond", json=data).json()
    assert result[0][0] == 'program_y', print(result)


if __name__ == '__main__':
    main()
