# Quick script to format google translate output to python dictionary

with open("en.txt") as en, open("es.txt") as es, open("se.txt") as se:
    es_lines = es.read().splitlines()
    se_lines = se.read().splitlines()

    out_es = []
    out_en = []
    out_se = []
    for index, source in enumerate(en.read().splitlines()):

        out_en.append(f'"{source}": "{source}",')
        out_es.append(f'"{source}": "{es_lines[index]}",')
        out_se.append(f'"{source}": "{se_lines[index]}",')

    with open("convert_db_genres.py", "w", encoding="utf-8") as out:
        out.write('\n'.join(out_en) + '\n'.join(out_es) + '\n'.join(out_se))