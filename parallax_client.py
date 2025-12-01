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
            response.raise_for_status()
            
            full_content = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data: '):
                        data_str = decoded_line[6:]
                        if data_str == '[DONE]':
                            break
                        try:
                            data_json = json.loads(data_str)
                            content = data_json['choices'][0]['delta'].get('content', '')
                            full_content += content
                        except:
                            pass
            
            return full_content.strip()

        except requests.exceptions.RequestException as e:
            print(f"[ParallaxClient] Request Error: {e}")
            raise Exception(f"Connection failed: {e}")
        except Exception as e:
            print(f"[ParallaxClient] Error: {e}")
            raise e
