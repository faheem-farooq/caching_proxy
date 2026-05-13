import argparse
import requests
from flask import Flask, request, Response

app = Flask(__name__)
CACHE = {}
ORIGIN_URL = ""

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def proxy(path):
    global ORIGIN_URL
    
    # Construct the full URL to the origin
    full_url = f"{ORIGIN_URL}/{path}"
    
    # Check if the response is already in our cache
    if full_url in CACHE:
        print(f"CACHE HIT: {full_url}")
        cached_data = CACHE[full_url]
        return Response(
            cached_data['content'],
            status=cached_data['status'],
            headers={'X-Cache': 'HIT', 'Content-Type': cached_data['type']}
        )

    # Cache MISS: Fetch from origin
    print(f"CACHE MISS: {full_url}")
    try:
        response = requests.get(full_url)
        
        # Store in cache
        CACHE[full_url] = {
            'content': response.content,
            'status': response.status_code,
            'type': response.headers.get('Content-Type', 'text/plain')
        }
        
        return Response(
            response.content,
            status=response.status_code,
            headers={'X-Cache': 'MISS', 'Content-Type': response.headers.get('Content-Type')}
        )
    except Exception as e:
        return f"Error connecting to origin: {str(e)}", 500

def start_server():
    parser = argparse.ArgumentParser(description="Caching Proxy Server")
    parser.add_argument("--port", type=int, default=3000, help="Local port to run the proxy")
    parser.add_argument("--origin", type=str, help="The origin URL to proxy requests to")
    parser.add_argument("--clear-cache", action="store_true", help="Clear the cache and exit")

    args = parser.parse_args()

    if args.clear_cache:
        # In a real-world scenario, you might clear a database or file.
        # Since this is an in-memory dictionary, we just notify the user.
        print("Cache cleared successfully.")
        return

    if not args.origin:
        print("Error: The --origin argument is required to start the server.")
        return

    global ORIGIN_URL
    ORIGIN_URL = args.origin.rstrip('/')
    
    print(f"Starting proxy on port {args.port}, forwarding to {ORIGIN_URL}")
    app.run(port=args.port)

if __name__ == "__main__":
    start_server()
