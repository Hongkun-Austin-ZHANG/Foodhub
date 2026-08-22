import base64
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# Root directory of the backend project.
BASE_DIR = Path(__file__).resolve().parent.parent

# Local menu image used for this first Vision API test.
IMAGE_PATH = BASE_DIR / "samples" / "menu_test.jpg"


def encode_image(image_path: Path) -> str:
    """
    Convert a local image file into a Base64 string.

    This lets us send the image directly to the multimodal API
    without uploading it to a separate storage service.
    """
    with image_path.open("rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def main() -> None:
    """
    Run a minimal end-to-end Vision API test.

    Goal:
    Send one restaurant menu image to the model and print
    the menu information it can clearly read.
    """

    # Load API credentials and model settings from backend/.env.
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from backend/.env"
        )

    if not model:
        raise RuntimeError(
            "OPENAI_MODEL is missing from backend/.env"
        )

    if not IMAGE_PATH.exists():
        raise FileNotFoundError(
            f"Menu image not found: {IMAGE_PATH}"
        )

    client = OpenAI(api_key=api_key)

    image_base64 = encode_image(IMAGE_PATH)

    response = client.responses.create(
        model=model,
        input=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Read this restaurant menu image. "
                            "List the dish names, prices, and restaurant-written "
                            "descriptions that are clearly visible. "
                            "Do not infer ingredients that are not explicitly "
                            "written on the menu."
                        ),
                    },
                    {
                        "type": "input_image",
                        "image_url": (
                            f"data:image/jpeg;base64,{image_base64}"
                        ),
                    },
                ],
            }
        ],
    )

    print("\n=== FoodHub Vision Test ===\n")
    print(response.output_text)

    # Print token usage so we can review cost later.
    if response.usage:
        print("\n=== Usage ===")
        print(response.usage)


if __name__ == "__main__":
    main()