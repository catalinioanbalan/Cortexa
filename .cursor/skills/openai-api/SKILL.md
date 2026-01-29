---
name: openai-api
description: OpenAI API integration patterns for chat and embeddings. Use when implementing AI features, calling OpenAI models, or working with embeddings.
---

# OpenAI API Integration

## Setup (Sync Client - matches existing codebase)

```python
from openai import OpenAI
from config import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)
```

## Chat Completions

```python
response = client.chat.completions.create(
    model=settings.CHAT_MODEL,  # gpt-4o-mini
    messages=[
        {"role": "system", "content": "System prompt here"},
        {"role": "user", "content": user_input}
    ],
    temperature=0.7  # 0 for factual, 0.7+ for creative
)
result = response.choices[0].message.content
```

## Embeddings

```python
response = client.embeddings.create(
    model=settings.EMBEDDING_MODEL,  # text-embedding-3-large
    input=text  # or list of texts for batch
)
embedding = response.data[0].embedding
# For batch: [item.embedding for item in response.data]
```

## Structured Outputs (optional enhancement)

```python
from pydantic import BaseModel

class Interpretation(BaseModel):
    summary: str
    themes: list[str]
    confidence: float

response = client.beta.chat.completions.parse(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": content}],
    response_format=Interpretation
)
result: Interpretation = response.choices[0].message.parsed
```

## Error Handling

```python
import openai

try:
    response = client.chat.completions.create(...)
except openai.RateLimitError:
    time.sleep(60)
    # Retry
except openai.APIError as e:
    raise HTTPException(500, f"OpenAI error: {e}")
```

## Models (config.py)

- Chat: `gpt-4o-mini` (cost-effective)
- Embeddings: `text-embedding-3-large` (high accuracy)
