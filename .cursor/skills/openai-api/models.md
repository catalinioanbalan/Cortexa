# OpenAI Models Reference

## Chat Models

| Model | Use Case | Context | Cost |
|-------|----------|---------|------|
| gpt-4o | Complex reasoning, vision | 128K | $$$ |
| gpt-4o-mini | Simple tasks, high volume | 128K | $ |
| o1 | Deep reasoning, planning | 200K | $$$$ |
| o3-mini | Reasoning, cost-effective | 200K | $$ |

## Embedding Models

| Model | Dimensions | Use Case |
|-------|------------|----------|
| text-embedding-3-large | 3072 (configurable) | High accuracy |
| text-embedding-3-small | 1536 | Cost-effective |

## Vision Support

Models with vision: `gpt-4o`, `gpt-4o-mini`

Image formats: JPEG, PNG, WebP, GIF (non-animated)
Max size: 20MB
Detail levels: `low` (512px), `high` (up to 2048px)

## Structured Outputs

Use `client.beta.chat.completions.parse()` with Pydantic models.
Supported: All GPT-4o variants.
