from pathlib import Path
from urllib import request
import shutil
import string
import subprocess
import sys


def create_dir_and_copy(dir_name: str) -> Path:
    p = Path(f"../tmp/{dir_name}")
    p.mkdir(parents=True, exist_ok=True)

    app_dir = Path.cwd() / "app"
    for item in app_dir.iterdir():
        dest = p / "app" / item.name
        # print("src", item)
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)

    # Copy dependencies
    dependency_dir = p / Path("usr/local/bin")
    dependency_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2("/usr/local/bin/docker-explorer", dependency_dir)

    return p


def get_image(image: str):
    registry_url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/{image}:pull"

    try:
        # Make the GET request
        response = request.get(registry_url)

        # Check if the request was successful
        if response.status_code == 200:
            print("Response Content:")
            print(response.content)  # Print the raw response content
        else:
            print(f"Request failed with status code {response.status_code}")
            print(response.content)  # Print the raw response content

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    image = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]

    get_image(image)

    # Generate a secure random string
    characters = string.ascii_letters + string.digits
    random_hash = "".join(secrets.choice(characters) for _ in range(8))
    # Create working directory for the image
    working_dir = create_dir_and_copy(random_hash)

    unshare_command = ["unshare", "--pid", "--mount-proc", "--uts", "--fork"]

    process = subprocess.Popen(
        unshare_command + ["chroot", working_dir, command, *args],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Read the output from stdout and print it line by line
    for line in process.stdout:
        print(line.decode("utf-8"), end="")

    for line in process.stderr:
        print(line.decode("utf-8"), end="", file=sys.stderr)

    # Wait for the subprocess to finish
    return_code = process.wait()
    # print("Exit code", return_code)
    exit(return_code)


if __name__ == "__main__":
    main()
