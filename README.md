# FireTail Action for uploading API Specs

This GitHub Action will send a openapi/swagger spec to FireTails platform

#### Pre-requisites:

1. Have a FireTail Account - [FireTail SaaS Platform](https://firetail.app) 
2. Uploaded a collection to FireTail Platform - [How to Create a Collection](https://www.firetail.io/docs/create-a-collection)
3. Created an API Token - [How to Create an API Token](https://www.firetail.io/docs/create-an-api-token)
4. Set API Token in Action Secrets


```bash
    steps:
      - uses: FireTail-io/upload-api-spec-to-firetail-action@v1.0.0
        env:
          FIRETAIL_API_TOKEN: ${{secret.FIRETAIL_API_TOKEN}}
          COLLECTION_UUID: <Set Collection UUID here>
          API_SPEC_LOCATION: "specfile/oas.yaml"
```
