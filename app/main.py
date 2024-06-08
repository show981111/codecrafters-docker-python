import json
from pathlib import Path
import urllib.request
import urllib.error
import urllib.parse
import shutil
import string
import subprocess
import sys
import secrets
import tarfile


def create_dir_and_copy(dir_name: str) -> Path:
    p = Path(Path(__file__).parent.parent / f"tmp/{dir_name}")
    p.mkdir(parents=True, exist_ok=True)

    app_dir = Path(__file__).parent
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


def get_image(image: str, output_dir: Path):
    try:
        image_info = image.split(":")
        image_name = image_info[0]
        image_version = "latest" if len(image_info) == 1 else image_info[1]

        registry_url = f"https://auth.docker.io/token?service=registry.docker.io&scope=repository:library/{image_name}:pull"
        manifest_url = f"https://registry.hub.docker.com/v2/library/{image_name}/manifests/{image_version}"

        token = ""
        # Get Token
        with urllib.request.urlopen(registry_url) as response:
            # Read the response content
            response_content = response.read()
            json_content = json.loads(response_content)
            token = json_content["token"]

        # Get manifest
        manifest_request = urllib.request.Request(manifest_url)
        manifest_request.add_header(
            "Accept", "application/vnd.docker.distribution.manifest.v2+json"
        )
        manifest_request.add_header("Authorization", f"Bearer {token}")
        with urllib.request.urlopen(manifest_request) as response:
            response_content = response.read()
            json_content = json.loads(response_content)

            # print("Json", json_content)

            # Pulling layers
            for layer in json_content["layers"]:
                layer_req = urllib.request.Request(
                    f"https://registry.hub.docker.com/v2/library/{image_name}/blobs/{layer['digest']}"
                )
                layer_req.add_header("Authorization", f"Bearer {token}")

                layer_path = Path(f"../tmp/docker/{image_name}_{image_version}")
                layer_path.mkdir(parents=True, exist_ok=True)
                print("Pulling...", layer["digest"], " --> ", layer_path)
                with open(layer_path / f"{layer['digest']}.tar", "wb") as f:
                    with urllib.request.urlopen(layer_req) as layer_response:
                        f.write(layer_response.read())

                for file in layer_path.iterdir():
                    ff = tarfile.open(file)
                    ff.extractall(output_dir)

    except urllib.error.HTTPError as e:
        print(f"HTTP error occurred: {e.code} - {e.reason}")
    except urllib.error.URLError as e:
        print(f"URL error occurred: {e.reason}")
    except Exception as e:
        print(f"An error occurred: {e}")


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage
    image = sys.argv[2]
    command = sys.argv[3]
    args = sys.argv[4:]

    # Generate a secure random string
    characters = string.ascii_letters + string.digits
    random_hash = "".join(secrets.choice(characters) for _ in range(8))
    # Create working directory for the image
    working_dir = create_dir_and_copy(random_hash)
    get_image(image, working_dir)

    # for file in working_dir.iterdir():
    #     print(file.name)

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
