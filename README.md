# FireTail Action for uploading API Specs

This GitHub Action will send an OpenAPI/Swagger specification to FireTail's platform

**Prerequisites:**

1. Active FireTail account - [FireTail SaaS Platform](https://firetail.app) 
2. API collection - [How to Create a Collection](https://www.firetail.io/docs/create-a-collection)
3. API Token - [How to Create an API Token](https://www.firetail.io/docs/create-an-api-token)
4. API token defined in GitHub - [Encrypted secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

```yaml
steps:
  - uses: actions/checkout@v3
  - uses: FireTail-io/upload-api-spec-to-firetail-action@v1.0.3
    env:
      FIRETAIL_API_TOKEN: ${{ secrets.FIRETAIL_API_TOKEN }}
      COLLECTION_UUID: ${{ env.COLLECTION_UUID }}
      API_SPEC_LOCATION: src/openapi-spec.yaml
      CONTEXT: ${{ toJson(github) }}
```
