import pickle

files = ['PFC', 'LH', 'RH', 'HC']
for f in files:
    try:
        with open(f'paradox_brain/{f}.para', 'rb') as fp:
            data = pickle.load(fp)
        payloads = data.get('payloads', {})
        vectors = data.get('vectors', {})
        first_key = list(payloads.keys())[0] if payloads else 'N/A'
        first_vec = vectors.get(first_key, [])
        print(f'{f}.para -> topics:{len(payloads)} | vector_dim:{len(first_vec)} | sample_topic:"{first_key}"')
        print(f'  vector_sample: {first_vec[:5]}')
        print(f'  raw_text_len:  {len(payloads.get(first_key, ""))} chars')
        print()
    except Exception as e:
        print(f'{f}.para ERROR: {e}')
