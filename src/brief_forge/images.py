from pathlib import Path
import base64
import requests
from openai import OpenAI
from PIL import Image, ImageOps

STYLE = (
    "Premium editorial technology illustration for a university computer-science news presentation. "
    "Consistent visual identity: deep midnight navy and charcoal palette, restrained teal and cyan "
    "highlights, cinematic but realistic lighting, sophisticated magazine-art direction, clean "
    "composition, strong focal subject, subtle depth, professional and intellectually curious mood. "
    "Widescreen composition with important subject matter centered safely. Absolutely no text, letters, "
    "numbers, logos, watermarks, captions, UI screenshots, borders or slide layouts."
)

def generate_slide_image(slide, index, settings, destination: Path):
    kwargs = {"api_key": settings.image_api_key}
    if settings.image_base_url:
        kwargs["base_url"] = settings.image_base_url
    client = OpenAI(**kwargs)
    prompt = (
        STYLE + "\n\nIllustrate this slide concept: "
        + str(slide.get("visual_concept", slide.get("title", "technology")))
        + "\nCommunicate the concept visually without written language."
    )
    result = client.images.generate(
        model=settings.image_model, prompt=prompt, size=settings.image_size
    )
    item = result.data[0]
    if getattr(item, "b64_json", None):
        destination.write_bytes(base64.b64decode(item.b64_json))
    elif getattr(item, "url", None):
        response = requests.get(item.url, timeout=120)
        response.raise_for_status()
        destination.write_bytes(response.content)
    else:
        raise RuntimeError("Image API returned neither b64_json nor a URL.")
    if destination.stat().st_size < 1000:
        raise RuntimeError(f"Generated image appears empty: {destination}")
    # Crop the provider's image to a true 16:9 canvas without distorting the subject.
    with Image.open(destination) as image:
        image = image.convert("RGB")
        fitted = ImageOps.fit(image, (1600, 900), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
        fitted.save(destination, format="PNG", optimize=True)
    return destination
