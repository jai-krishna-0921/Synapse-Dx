from qdrant_client import QdrantClient

client = QdrantClient(url='http://localhost:6333')

# Get a sample point to see the structure
points, next_offset = client.scroll(collection_name='med_guidelines', limit=3)

print("Sample Qdrant Document Structure:")
print("=" * 80)

for i, point in enumerate(points, 1):
    print(f"\nDocument {i}:")
    print(f"  ID: {point.id}")
    print(f"  Payload keys: {list(point.payload.keys())}")
    print(f"  Payload:")
    for key, value in point.payload.items():
        if isinstance(value, str) and len(value) > 100:
            print(f"    {key}: {value[:100]}...")
        else:
            print(f"    {key}: {value}")
    print("-" * 80)

print("\nAgno Knowledge expects documents to have a 'name' field in payload.")
print("Check if 'name' is in the payload keys above.")
