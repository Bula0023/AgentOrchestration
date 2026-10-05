from .schemas import APICallInput, APICallOutput
import httpx 

def call_api(args: APICallInput) -> APICallOutput:
    response = httpx.request(
        method=args.method,
        url= args.url,
        json=args.body,
        timeout=10,
    )
    try: 
        data = response.json()
    except ValueError:
        data = response.text
    return APICallOutput(status_code=response.status_code, data=data)