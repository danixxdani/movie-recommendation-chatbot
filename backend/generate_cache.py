# backend/generate_cache.py
import pandas as pd
import numpy as np
import pickle
from openai import OpenAI
from dotenv import load_dotenv
import os

# .env 파일 로드
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 파일 경로 설정 (프로젝트 루트 기준으로)
CSV_FILE = "../data/movies_keywords.csv"
CACHE_FILE = "keyword_cache.pkl"

def create_embedding_cache():
    try:
        df = pd.read_csv(CSV_FILE)
    except FileNotFoundError:
        print(f"Error: {CSV_FILE} not found. Please ensure the CSV file is in the 'data/' directory.")
        return

    # CSV에 'keyword' 컬럼이 있다고 가정
    keywords = df['keyword'].unique().tolist()
    
    if not keywords:
        print("No keywords found in the CSV file. Please check the 'keyword' column.")
        return

    print(f"{len(keywords)}개의 키워드 임베딩 중... 이 과정은 시간이 소요될 수 있습니다.")
    
    # OpenAI 임베딩 생성 (비용 절감을 위해 배치 처리)
    # 한 번에 2048개까지 임베딩 가능
    batch_size = 2048
    all_vectors = []
    for i in range(0, len(keywords), batch_size):
        batch_keywords = keywords[i:i + batch_size]
        try:
            response = client.embeddings.create(
                input=batch_keywords,
                model="text-embedding-3-small"
            )
            batch_vectors = [data.embedding for data in response.data]
            all_vectors.extend(batch_vectors)
            print(f"  {len(all_vectors)} / {len(keywords)} 키워드 임베딩 완료.")
        except Exception as e:
            print(f"임베딩 중 오류 발생: {e}")
            print(f"현재까지 {len(all_vectors)}개 키워드만 임베딩되었습니다.")
            break # 오류 발생 시 중단
    
    if not all_vectors:
        print("임베딩된 벡터가 없습니다. API 키와 네트워크 연결을 확인하세요.")
        return

    # 키워드와 벡터를 매핑하여 딕셔너리로 저장
    cache_data = {
        "keywords": keywords,
        "vectors": np.array(all_vectors).astype('float32')
    }
    
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache_data, f)
    
    print(f"캐시 파일 '{CACHE_FILE}' 생성 완료!")

if __name__ == "__main__":
    create_embedding_cache()