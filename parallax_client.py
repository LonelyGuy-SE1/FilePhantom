import requests
import json
import config

class ParallaxClient:
    def __init__(self):
        self.api_url = config.PARALLAX_API_URL
        self.timeout = config.PARALLAX_TIMEOUT

    def get_completion(self, messages: list) -> str:
        payload = {
            "messages": messages,
            "max_tokens": 1024,
            "stream": True
        }

        try:
            response = requests.post(
                self.api_url, 
                headers={"Content-Type": "application/json"}, 
                json=payload, 
                timeout=self.timeout,
                stream=True
            )

            print(f"[ParallaxClient] Response status: {response.status_code}")
            response.raise_for_status()
            
            full_content = ""
            api_error = None
            
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    
                    if decoded_line.startswith('data: '):
                        data_str = decoded_line[6:]
                        if data_str == '[DONE]':
                            print(f"[ParallaxClient] Received [DONE] signal")
                            break
                        try:
                            data_json = json.loads(data_str)
                            
                            # Detect API error in chunk
                            if 'error' in data_json:
                                api_error = data_json['error']
                                print(f"[ParallaxClient] API Error detected: {api_error}")
                                break
                            
                            content = data_json['choices'][0]['delta'].get('content', '')
                            if content:
                                chunk_count += 1
                                full_content += content
                        except Exception as e:
                            if line_count <= 5:
                                print(f"[ParallaxClient] Failed to parse chunk: {e}")
            
            print(f"[ParallaxClient] Received {line_count} lines, {chunk_count} content chunks")
            print(f"[ParallaxClient] Total content length: {len(full_content)} chars")
            
            # If no content chunks found, print a few received lines for diagnosis
            if chunk_count == 0 and line_count > 10:
                print(f"[ParallaxClient] WARNING: Got {line_count} lines but 0 content chunks!")
                print(f"[ParallaxClient] First few lines:")
                for i, debug_line in enumerate(debug_lines, 1):
                    print(f"  {i}: {debug_line}")
            
            # If API returned an error, raise an exception
            if api_error:
                error_msg = api_error.get('message', str(api_error))
                raise Exception(f"API Error: {error_msg}")
            
            return full_content.strip()

        except requests.exceptions.RequestException as e:
            print(f"[ParallaxClient] Request Error: {e}")
            raise Exception(f"Connection failed: {e}")
        except Exception as e:
            print(f"[ParallaxClient] Error: {e}")
            raise e
