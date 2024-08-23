import typesense
from .config import settings, TYPESENSE_COLLECTION_NAME

# Initialize Typesense client
client = typesense.Client(
    {
        "nodes": [
            {
                "host": settings.typesense_host,
                "port": settings.typesense_port,
                "protocol": settings.typesense_protocol,
            }
        ],
        "api_key": settings.typesense_api_key,
        "connection_timeout_seconds": settings.typesense_connection_timeout_seconds,
    }
)

# Define the schema for the Typesense collection
schema = {
    "name": TYPESENSE_COLLECTION_NAME,
    "enable_nested_fields": True,
    "fields": [
        {"name": "filepath", "type": "string", "infix": True},
        {"name": "filename", "type": "string", "infix": True},
        {"name": "size", "type": "int32"},
        {"name": "file_created_at", "type": "int64", "facet": False},
        {"name": "created_date", "type": "string", "facet": True, "optional": True, "sort": True},
        {"name": "created_month", "type": "string", "facet": True, "optional": True, "sort": True},
        {"name": "created_year", "type": "string", "facet": True, "optional": True, "sort": True},
        {"name": "file_last_modified_at", "type": "int64", "facet": False},
        {"name": "file_type", "type": "string", "facet": True},
        {"name": "file_type_group", "type": "string", "facet": True},
        {"name": "last_scan_at", "type": "int64", "facet": False, "optional": True},
        {"name": "library_id", "type": "int32", "facet": True},
        {"name": "folder_id", "type": "int32", "facet": True},
        {
            "name": "tags",
            "type": "string[]",
            "facet": True,
            "optional": True,
            "locale": "zh"
        },
        {
            "name": "metadata_entries",
            "type": "object[]",
            "optional": True,
            "locale": "zh",
        },
        {"name": "metadata_text", "type": "string", "optional": True, "locale": "zh"},
        {
            "name": "embedding",
            "type": "float[]",
            "embed": {
                "from": ["filepath", "filename", "metadata_text"],
                "model_config": {
                    "model_name": "openai/shaw/dmeta-embedding-zh",
                    "api_key": "xxx",
                    "url": "http://localhost:11434"
                }
            },
            "optional": True,       
        },
    ],
    "token_separators": [":", "/", " ", "\\"],
}


def update_collection_fields(client, schema):
    existing_collection = client.collections[TYPESENSE_COLLECTION_NAME].retrieve()
    existing_fields = {field["name"]: field for field in existing_collection["fields"]}
    new_fields = {field["name"]: field for field in schema["fields"]}

    fields_to_add = []
    for name, field in new_fields.items():
        if name not in existing_fields:
            fields_to_add.append(field)
        else:
            # Check if the field can be updated
            updatable_properties = ["facet", "optional"]
            for prop in updatable_properties:
                if prop in field and field[prop] != existing_fields[name].get(prop):
                    fields_to_add.append(field)
                    break

    if fields_to_add:
        client.collections[TYPESENSE_COLLECTION_NAME].update({"fields": fields_to_add})
        print(
            f"Added/updated {len(fields_to_add)} fields in the '{TYPESENSE_COLLECTION_NAME}' collection."
        )
    else:
        print(
            f"No new fields to add or update in the '{TYPESENSE_COLLECTION_NAME}' collection."
        )


if __name__ == "__main__":
    import sys

    force_recreate = "--force" in sys.argv

    try:
        # Check if the collection exists
        existing_collection = client.collections[TYPESENSE_COLLECTION_NAME].retrieve()

        if force_recreate:
            client.collections[TYPESENSE_COLLECTION_NAME].delete()
            print(
                f"Existing Typesense collection '{TYPESENSE_COLLECTION_NAME}' deleted successfully."
            )
            client.collections.create(schema)
            print(
                f"Typesense collection '{TYPESENSE_COLLECTION_NAME}' recreated successfully."
            )
        else:
            # Update the fields of the existing collection
            update_collection_fields(client, schema)

    except typesense.exceptions.ObjectNotFound:
        # Collection doesn't exist, create it
        client.collections.create(schema)
        print(
            f"Typesense collection '{TYPESENSE_COLLECTION_NAME}' created successfully."
        )

    except Exception as e:
        print(f"An error occurred: {str(e)}")
