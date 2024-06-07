from pathlib import Path
import secrets
import shutil
import string


def create_dir_and_copy(dir_name: str) -> Path:
    p = Path(f"../tmp/{dir_name}")
    p.mkdir(parents=True, exist_ok=True)

    parent_dir = Path.cwd()
    for item in parent_dir.iterdir():
        dest = p / "app" / item.name
        if item.is_dir():
            shutil.copytree(item, dest)
        else:
            shutil.copy2(item, dest)
    return p


def main():
    # You can use print statements as follows for debugging, they'll be visible when running tests.
    # print("Logs from your program will appear here!")

    # Uncomment this block to pass the first stage

    # command = sys.argv[3]
    # args = sys.argv[4:]

    # Generate a secure random string
    characters = string.ascii_letters + string.digits
    random_hash = "".join(secrets.choice(characters) for _ in range(8))
    # Create working directory for the image
    working_dir = create_dir_and_copy(random_hash)

    # process = subprocess.Popen(
    #     ["chroot", working_dir, command, *args],
    #     stdout=subprocess.PIPE,
    #     stderr=subprocess.PIPE,
    # )

    # # Read the output from stdout and print it line by line
    # for line in process.stdout:
    #     print(line.decode("utf-8"), end="")

    # for line in process.stderr:
    #     print(line.decode("utf-8"), end="", file=sys.stderr)

    # # Wait for the subprocess to finish
    # return_code = process.wait()
    # exit(return_code)


if __name__ == "__main__":
    main()
