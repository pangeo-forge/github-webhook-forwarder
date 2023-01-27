from fastapi import FastAPI, HTTPException, Request, status
from pydantic import BaseModel

app = FastAPI()


class GitHubLabel(BaseModel):
    name: str


@app.post("/", status_code=status.HTTP_200_OK)
async def forwarder(request: Request):
    """
    
    """

    event = request.headers.get("X-GitHub-Event")
    print(f"{event = }")

    request_json = await request.json()

    if event == "pull_request":
        labels = [
            GitHubLabel(**label)
            for label in request_json["pull_request"]["labels"]
        ]
        if not labels:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No labels."
            )

        forward_to = [
            l.name.split("fwd:")[-1]
            for l in labels
            if l.name.startswith("fwd:")
        ]
        if not forward_to:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No labels starting with 'fwd:'",
            )

    for recipient in forward_to:
        print(f"Forwarding GitHub webhook to {recipient = }")
        # FIXME: use httpx to make this request (aiohttp doesnt work w python 3.11)
        # async with aiohttp.ClientSession() as session:
        #     async with session.post(
        #            f"https://{recipient}",
        #            headers=request.headers,
        #            json=request_json,
        #        ) as response:
        #            ...

    return f"Forwarded to {forward_to}"
