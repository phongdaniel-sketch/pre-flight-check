from urllib.parse import urlparse, parse_qs

def extract_video_id(url: str) -> str:
    try:
        parsed = urlparse(url)
        # 1. Try 'vid' query param (Common in TikTok CDN)
        query_params = parse_qs(parsed.query)
        if 'vid' in query_params:
            return query_params['vid'][0]
        
        # 2. Fallback: Last path segment (ignoring extension)
        path_segments = parsed.path.split("/")
        filename = path_segments[-1] if path_segments else "unknown"
        return filename.split(".")[0]
    except:
        return "unknown_video_id"

def test_parsing():
    complex_url = "https://v16-tt4b.tiktokcdn.com/b8ce63b082175af50e8e876b576b1840/696f323d/video/tos/alisg/tos-alisg-ve-0051c001-sg/okMPgAIGV6eGbgSA6jfHMAMRvvLJ82AB4xFefA/?a=1233&vid=v10033g50000d30vju7og65o7bpodg1g&br=23318"
    simple_url = "http://localhost:8000/static/uploads/myvideo.mp4"
    
    id1 = extract_video_id(complex_url)
    print(f"Complex URL ID: {id1}")
    assert id1 == "v10033g50000d30vju7og65o7bpodg1g"
    
    id2 = extract_video_id(simple_url)
    print(f"Simple URL ID: {id2}")
    assert id2 == "myvideo"
    
    print("✅ All Parsing Tests Passed")

if __name__ == "__main__":
    test_parsing()
