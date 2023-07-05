# FireTail Action for uploading API Specs


```bash
    steps:
      - uses: FireTail-io/upload-api-spec-to-firetail@dev
        env:
          FIRETAIL_API_TOKEN: ${{secret.FIRETAIL_API_TOKEN}}
          COLLECTION_UUID: ${{env.COLLECTION_UUID}}
          API_SPEC_LOCATION: "specfile/oas.yaml"
```
