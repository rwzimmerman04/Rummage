from searcher import search_index
matches = search_index("holy knight", "../.index")
    

print(f"Found {len(matches)} results:")
for m in matches:
    print(m["filename"], m["page"], m["snippet"])
