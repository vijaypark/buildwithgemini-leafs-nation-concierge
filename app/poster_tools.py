"""Vintage Game Day Poster Generation Tool for Leafs Nation Concierge."""

import time
from typing import Any, Dict
from google import genai
from google.adk.tools import ToolContext
from google.cloud import storage
from google.genai import types

PROJECT_ID = "qwiklabs-gcp-04-c873db07994b"
BUCKET_NAME = "leafs-nation-concierge-assets-c873db"
IMAGE_MODEL = "gemini-3.1-flash-lite-image"
IMAGE_REGION = "global"


async def generate_vintage_game_poster(
    opponent: str,
    tool_context: ToolContext,
    game_date: str = "Tonight",
    venue: str = "Scotiabank Arena, Toronto",
) -> Dict[str, Any]:
    """Generate a vintage retro silkscreen game-day match poster for Toronto Maple Leafs vs. an opponent.

    Uses gemini-3.1-flash-lite-image in the global region.
    1. Saves the image with tool_context.save_artifact so it appears in the Playground's Artifacts panel.
    2. Uploads the image bytes to the public Cloud Storage bucket and returns its public HTTPS URL.

    Args:
        opponent: The opponent hockey team (e.g. 'Montreal Canadiens', 'Boston Bruins', 'Edmonton Oilers').
        tool_context: The ADK ToolContext for managing artifacts and session metadata.
        game_date: The date or time label for the match (e.g. 'October 10, 2026' or 'Saturday Night 7 PM').
        venue: The game arena venue.

    Returns:
        A dictionary with the public image URL, matchup info, and status.
    """
    prompt = (
        f"A vintage 1940s-1950s Canadian hockey game-day match poster. "
        f"Bold retro typography reading 'TORONTO MAPLE LEAFS VS {opponent.upper()}'. "
        f"Stylized graphic hockey players in classic royal blue and white Maple Leafs uniform facing {opponent}. "
        f"Text accents: '{game_date}', '{venue}'. "
        f"Vintage textured paper, silkscreen screenprint aesthetic, rich contrast, dynamic action composition, classic NHL nostalgia poster art."
    )

    try:
        # Initialize Vertex AI GenAI Client in the global region
        client = genai.Client(vertexai=True, project=PROJECT_ID, location=IMAGE_REGION)

        response = client.models.generate_content(
            model=IMAGE_MODEL,
            contents=prompt,
        )

        image_bytes = None
        mime_type = "image/jpeg"

        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            for part in response.candidates[0].content.parts:
                if getattr(part, "inline_data", None) and part.inline_data.data:
                    image_bytes = part.inline_data.data
                    mime_type = part.inline_data.mime_type or "image/jpeg"
                    break

        if not image_bytes:
            return {"status": "error", "message": "No image data returned from image generation model."}

        slug_opp = opponent.lower().replace(" ", "-")
        timestamp = int(time.time())
        ext = "png" if "png" in mime_type else "jpg"
        filename = f"vintage-poster-leafs-vs-{slug_opp}-{timestamp}.{ext}"

        # 1. Save with tool_context.save_artifact for Playground Artifacts panel
        artifact_part = types.Part.from_bytes(data=image_bytes, mime_type=mime_type)
        await tool_context.save_artifact(
            filename=filename,
            artifact=artifact_part,
            custom_metadata={
                "type": "game_day_poster",
                "matchup": f"Leafs vs {opponent}",
                "date": game_date,
            },
        )

        # 2. Upload same bytes directly to public GCS bucket (no local file written)
        storage_client = storage.Client(project=PROJECT_ID)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob_name = f"posters/{filename}"
        blob = bucket.blob(blob_name)
        blob.upload_from_string(image_bytes, content_type=mime_type)

        public_url = f"https://storage.googleapis.com/{BUCKET_NAME}/{blob_name}"

        return {
            "status": "success",
            "image_url": public_url,
            "artifact_filename": filename,
            "matchup": f"Toronto Maple Leafs vs {opponent}",
            "game_date": game_date,
            "venue": venue,
            "style": "1940s Retro Silkscreen Match Poster",
            "message": f"Poster generated, saved to artifacts, and uploaded to {public_url}",
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to generate vintage poster: {str(e)}",
        }
