from django.conf import settings
from google import genai
from .database import cache_response
import json
import io

import re


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models" 

config_json = io.open("config.json").read()
config = json.loads(config_json)

def assess(query):
    system_prompt, custom_prompt = parse_prompts()
    prompt = f"""
    ##BEGIN MAIN PROMPT## This is the most important part of your prompt.
    ${system_prompt}
    ##END MAIN PROMPT##

    ##BEGIN COMPANY PROMPT## This is the criteria that the company requires software to follow.
    ${custom_prompt}
    ##END COMPANY PROMPT##

    ##BEGIN USER PROMPT## This contains the name or an url to a piece of software
    ${query}
    ##END USER PROMPT##
    """
    response = call_gemini(prompt)
    cache_response(query, response)
    return response

def parse_prompts():
    return io.open("reconradar/assessor/prompt.txt").read(), io.open("custom_prompt.txt").read()


def call_gemini(prompt):
    """
    Calls the Gemini API using Google's genai library.

    Args:
        prompt (str): The text prompt to send to the model.

    Returns:
        str: The generated text response, or an error message.
    """

    client = genai.Client(api_key=config["api_key"])
    response = client.models.generate_content(
        model=config["model"],
        contents=prompt
    )
    print(response.text)
    return response.text




SEPARATOR = "¤¤¤¤"

def split(raw):
    """
    gets the 5-part content → splits it → validates it.
    Returns:
       [part1, part2, part3, part4]  (markdown sections)
       scores_dict (for radar chart)
    """

    # ---- Split into 6 parts ----
    parts = raw.split(SEPARATOR)
    if len(parts) != 6:
        raise ValueError(f"Expected 6 sections separated by {SEPARATOR}, got {len(parts)}")


    # Clean whitespace on each
    parts = [p.strip() for p in parts]

    # ---- Parse CSV Score Line (section 5) ----
    score_line = parts[4]

    if not re.match(r"^\d{1,3},\d{1,3},\d{1,3},\d{1,3},\d{1,3},\d{1,3}$", score_line):
        raise ValueError(f"Invalid score format: {score_line}")

    nums = list(map(int, score_line.split(",")))

    scores = {
        "security": nums[0],
        "compliance": nums[1],
        "reputation": nums[2],
        "controls": nums[3],
        "privacy": nums[4],
        "reliability": nums[5],
    }

    # ---- Parse Metadata (Section 6) ----
    meta_line = parts[5].strip()

    # Format: category,site,vendor,name_version
    meta_parts = meta_line.split("½")

    if len(meta_parts) != 4:
        raise ValueError(f"Invalid metadata format: {meta_line}")

    metadata = {
        "category": meta_parts[0],
        "site": meta_parts[1],
        "vendor": meta_parts[2],
        "name_version": meta_parts[3],
    }

    #return parts[:4], scores
    return parts[:4], scores, metadata
