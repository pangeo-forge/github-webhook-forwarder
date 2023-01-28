import httpx
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
    request_bytes = await request.body()

    if event == "pull_request":
        label_containing_obj = "pull_request"
    elif event == "issue_comment":
        label_containing_obj = "issue"
    else:
        raise NotImplementedError

    labels = [
        GitHubLabel(**label)
        for label in request_json[label_containing_obj]["labels"]
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

    responses = {}
    for recipient in forward_to:
        print(f"Forwarding GitHub webhook to {recipient = }")
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"https://{recipient}",
                headers={
                    "X-GitHub-Event": request.headers.get("X-GitHub-Event"),
                    "X-Hub-Signature-256": request.headers.get("X-Hub-Signature-256"),
                },
                data=request_bytes,
            )
            print(f"{recipient = } responded with {r.status_code = }")
            responses |= {recipient: r.status_code}

    return f"Forwarded to {responses}"
