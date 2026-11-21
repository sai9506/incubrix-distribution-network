
import sys
from pathlib import Path

# Add project root to Python import path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.storage.object_storage import storage


def main():

    test_file = PROJECT_ROOT / "storage_test.txt"
    download_file = PROJECT_ROOT / "storage_download.txt"

    try:
        print("\n1. Checking storage bucket...")

        result = storage.create_bucket()
        print(result)

        print("\n2. Creating test file...")

        test_content = "IncuBrix object storage integration test."

        test_file.write_text(
            test_content,
            encoding="utf-8"
        )

        print("\n3. Uploading file...")

        result = storage.upload_file(
            "test/storage_test.txt",
            str(test_file)
        )
        print(result)

        print("\n4. Listing stored files...")

        files = storage.list_files()

        for file in files:
            print(file)

        print("\n5. Downloading file...")

        result = storage.download_file(
            "test/storage_test.txt",
            str(download_file)
        )
        print(result)

        print("\n6. Verifying downloaded content...")

        downloaded_content = download_file.read_text(
            encoding="utf-8"
        )

        assert downloaded_content == test_content

        print("\nStorage integration test passed!")

    finally:
        for file in [test_file, download_file]:
            if file.exists():
                file.unlink()


if __name__ == "__main__":
    main()
