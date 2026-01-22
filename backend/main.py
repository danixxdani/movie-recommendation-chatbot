import numpy as np
import pickle
from openai import OpenAI
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import uvicorn

# 1. Load environment variables and OpenAI setup
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found.")

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI()

# Add CORS middleware (Important!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow access from Streamlit app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Load keyword database (cache)
CACHE_FILE = "keyword_cache.pkl"
try:
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
        ALL_KEYWORDS = cache["keywords"]
        KEYWORD_VECTORS = cache["vectors"]
    print(f"✅ DB loaded successfully: {len(ALL_KEYWORDS)} keywords ready.")
except Exception as e:
    print(f"❌ Cache loading failed: {e}")
    ALL_KEYWORDS = []
    KEYWORD_VECTORS = np.array([])

class RecommendRequest(BaseModel):
    user_input: str

@app.get("/")
async def root():
    return {"message": "CineMatch Backend API is running!"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "keywords_loaded": len(ALL_KEYWORDS),
        "openai_configured": bool(OPENAI_API_KEY)
    }

@app.post("/recommend")
async def recommend_movies(request: RecommendRequest):
    if not ALL_KEYWORDS or KEYWORD_VECTORS.size == 0:
        raise HTTPException(status_code=500, detail="Server keyword database is empty.")

    try:
        # print(f"\n{'='*60}")
        # print(f"📥 NEW QUERY: {request.user_input}")
        # print(f"{'='*60}")
        
        # --- Step 1: Intent Expansion with Core Preservation ---
        prompt_1 = f"""
        User Input: "{request.user_input}"
        
        Task: Expand the user's input into 10 specific cinematic keywords while PRESERVING core concepts.
        
        CRITICAL RULES:
        1. IDENTIFY CORE KEYWORDS: Extract the main nouns, genres, or themes from the user's input (e.g., "family", "love", "thriller", "90s")
        2. PRESERVE CORE KEYWORDS: If the user explicitly mentions "family", "romance", "horror", etc., AT LEAST 50% of your output must include or directly relate to that core concept
        3. EXPAND APPROPRIATELY: Add related emotional tones, sub-genres, or narrative elements that ENHANCE the core concept, not replace it
        4. USE PROFESSIONAL TERMINOLOGY: Convert casual language to film industry terms (e.g., "sad" → "Melancholic", "funny" → "Comedic")
        5. MEDIA TYPE PRESERVATION: If the user asks for a "Movie", focus ONLY on film-related terms. Avoid TV-related terms like "Drama", "Series", or "K-Drama" unless the user explicitly asked for them.
        
        Examples:
        - Input: "Feel-good family film" → Output must include: "Family", "Family-friendly", "Family bonding", "Wholesome", "All-ages", etc.
        - Input: "Intense love stories" → Output must include: "Romance", "Romantic", "Love", "Passionate", "Star-crossed", etc.
        - Input: "90s nostalgia" → Output must include: "90s", "1990s", "Nostalgia", "Retro", etc.
        
        Output ONLY 10 keywords/phrases separated by commas. Ensure the core concept is clearly maintained.
        """
        
        response_1 = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a film keyword specialist. Your primary job is to PRESERVE the user's core intent while expanding it with relevant professional terminology. Never lose the main concept."},
                {"role": "user", "content": prompt_1}
            ]
        )
        llm_expanded_keywords = [k.strip() for k in response_1.choices[0].message.content.split(",") if k.strip()]
        
        # print(f"\n🔍 Step 1 - Expanded Keywords:")
        # print(f"\n{response_1.choices[0].message.content}")

        # --- Step 2: Broad Semantic Retrieval ---
        query_resp = client.embeddings.create(input=llm_expanded_keywords, model="text-embedding-3-small")
        query_vectors = np.array([d.embedding for d in query_resp.data]).astype('float32')
        
        similarities = cosine_similarity(query_vectors, KEYWORD_VECTORS)
        
        candidates = set()
        for row in similarities:
            top_indices = row.argsort()[-5:][::-1]
            for idx in top_indices:
                if row[idx] >= 0.45:
                    candidates.add(ALL_KEYWORDS[idx])
        
        candidate_list = list(candidates)
        
        # print(f"\n🎯 Step 2 - Database Candidates Found: {len(candidate_list)}")
        # print(f"  {', '.join(sorted(candidate_list))}")
        
        if not candidate_list:
            print(f"\n⚠️  No candidates found in database")
            return {"recommended_keywords": [], "llm_generated_keywords": llm_expanded_keywords}

        # --- Step 3: Context-Aware Filtering & Combination ---
        verification_prompt = f"""
        User's Original Intent: "{request.user_input}"
        Database Candidates: {", ".join(candidate_list)}

        CRITICAL RULE: 
        - A keyword is valid ONLY if it covers the ENTIRE intent. 
        - If a candidate from the list only covers partially, you ARE FORBIDDEN from using it alone. You MUST combine it with another candidate using a '+' sign.
        - If the user specifies a media type (e.g., Movie or TV Series), you MUST NOT use keywords that are exclusive to the other format.

        Task:
        1. DECONSTRUCT INTENT: Break down the user's intent into its essential components.
        2. INTERSECTION PRINCIPLE: Every output keyword must represent the INTERSECTION of all essential components.
        3. COMBINATION LOGIC:
           - If a single keyword in 'Database Candidates' already captures the full intersection, use it.
           - Otherwise, you MUST create a combined term by joining a keyword for Component A and a keyword for Component B from the 'Database Candidates' using a ' + ' sign.
        4. ANTI-GENERALIZATION RULE: 
           - DO NOT return a keyword that only covers part of the intent. 
        5. SOURCE INTEGRITY: Use ONLY exact strings from 'Database Candidates'. Do not shorten or modify them except for joining with ' + '.
        6. SELECTION: Return 5-8 most relevant, high-precision keywords/combinations.
        7. FILTERING: Remove any candidate that is out of user's intent or is irrelevant.
        8. RANKING RULE: List the keywords in order of relevance to the "{request.user_input}".

        CRITICAL OUTPUT RULES:
        - Output ONLY the keywords separated by commas.
        - **DO NOT include any labels, core context, intros, or outros.**
        """
        
        verify_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[ 
                {"role": "system", "content": "You are a precision movie search filter. Your job is to eliminate ambiguous keywords that could apply to multiple genres when the user specified a specific context. to ensure the user's \"Primary Intent\" is preserved in every single keyword returned. Your response must be a single line of comma-separated strings."},
                {"role": "user", "content": verification_prompt}
            ]
        )
        
        final_keywords = [k.strip() for k in verify_response.choices[0].message.content.split(",") if k.strip()]
        
        # print(f"\n✅ Step 3 - Final Recommended Keywords:")
        # print(f"{verify_response.choices[0].message.content}")

        return {
            "recommended_keywords": sorted(final_keywords),
            "llm_generated_keywords": llm_expanded_keywords
        }

    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        raise HTTPException(status_code=500, detail="Internal Server Error")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
