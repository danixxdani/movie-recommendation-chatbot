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

# 1. 환경 변수 로드 및 OpenAI 설정
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY를 찾을 수 없습니다.")

client = OpenAI(api_key=OPENAI_API_KEY)
app = FastAPI()

# CORS 설정 추가 (중요!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Streamlit 앱에서 접근 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. 키워드 데이터베이스(캐시) 로드
CACHE_FILE = "keyword_cache.pkl"
try:
    with open(CACHE_FILE, "rb") as f:
        cache = pickle.load(f)
        ALL_KEYWORDS = cache["keywords"]
        KEYWORD_VECTORS = cache["vectors"]
    print(f"✅ DB 로드 완료: {len(ALL_KEYWORDS)}개의 키워드가 준비되었습니다.")
except Exception as e:
    print(f"❌ 캐시 로드 실패: {e}")
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
        raise HTTPException(status_code=500, detail="서버의 키워드 데이터베이스가 비어있습니다.")

    try:
        # --- Step 1: 의도 확장 (Intent Expansion with Core Preservation) ---
        prompt_1 = f"""
        User Input: "{request.user_input}"
        
        Task: Expand the user's input into 10 specific cinematic keywords while PRESERVING core concepts.
        
        CRITICAL RULES:
        1. IDENTIFY CORE KEYWORDS: Extract the main nouns, genres, or themes from the user's input (e.g., "family", "love", "thriller", "90s")
        2. PRESERVE CORE KEYWORDS: If the user explicitly mentions "family", "romance", "horror", etc., AT LEAST 50% of your output must include or directly relate to that core concept
        3. EXPAND APPROPRIATELY: Add related emotional tones, sub-genres, or narrative elements that ENHANCE the core concept, not replace it
        4. USE PROFESSIONAL TERMINOLOGY: Convert casual language to film industry terms (e.g., "sad" → "Melancholic", "funny" → "Comedic")
        
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

        # --- Step 2: 의미적 그물망 검색 (Broad Semantic Retrieval) ---
        query_resp = client.embeddings.create(input=llm_expanded_keywords, model="text-embedding-3-small")
        query_vectors = np.array([d.embedding for d in query_resp.data]).astype('float32')
        
        similarities = cosine_similarity(query_vectors, KEYWORD_VECTORS)
        
        candidates = set()
        for row in similarities:
            top_indices = row.argsort()[-5:][::-1]
            for idx in top_indices:
                if row[idx] >= 0.38:
                    candidates.add(ALL_KEYWORDS[idx])
        
        candidate_list = list(candidates)
        if not candidate_list:
            return {"recommended_keywords": [], "llm_generated_keywords": llm_expanded_keywords}

        # --- Step 3: 맥락 기반 정제 및 조합 (Context-Aware Filtering & Combination) ---
        verification_prompt = f"""
        User's Original Intent: "{request.user_input}"
        Database Candidates: {", ".join(candidate_list)}

        Task:
        1. Extract the CORE CONTEXT from the user's intent (e.g., if they said "intense love stories", the core context is LOVE/ROMANCE).
        2. From the Database Candidates, select 5-8 keywords that best match the intent.
        3. KEYWORD COMBINATION RULES:
           - If a generic keyword (e.g., "Intense", "Dark", "Emotional") exists AND a specific genre/context keyword (e.g., "Romantic Drama", "Thriller", "Romance") exists in the candidates:
             * Combine them if it clarifies the user's intent
             * Format combined keywords with a + sign: "Intense + Romantic Drama"
             * Only combine if BOTH words exist separately in the Database Candidates
           - If a keyword is already specific enough (e.g., "Star-Crossed Lovers"), keep it as is
           - Prefer combined keywords that remove ambiguity
        4. FILTERING RULES:
           - Reject standalone generic keywords that could apply to multiple genres outside the user's context
           - Example: For "intense love stories", reject bare "Intense" or "Second Chance" but accept "Intense + Romance" or "Second Chance at Love"
        5. Use ONLY words from the Database Candidates list (you can combine them with +, but don't invent new words).
        
        Return 5-8 final keywords separated by commas. Use the format "Keyword1 + Keyword2" for combined terms.
        Examples: "Intense + Romantic Drama", "Dark + Comedy", "Star-Crossed Lovers", "Forbidden Love"
        """
        
        verify_response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a precision movie search filter. Your job is to eliminate ambiguous keywords that could apply to multiple genres when the user specified a specific context."},
                {"role": "user", "content": verification_prompt}
            ]
        )
        
        final_keywords = [k.strip() for k in verify_response.choices[0].message.content.split(",") if k.strip()]

        return {
            "recommended_keywords": sorted(final_keywords),
            "llm_generated_keywords": llm_expanded_keywords
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
