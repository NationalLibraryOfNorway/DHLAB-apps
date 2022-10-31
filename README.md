# Web applications from NB DHLAB

This repo contains source code for various web applications provided by the DHLAB of the National Library of Norway. The web applications are hosted here: https://www.nb.no/dh-lab/apper

## Example usage

```bash
cd collocations
docker build -t nb-collocations .
docker run --rm -p 5001:5001 nb-collocations
```

# App URLs and source repos 

| Folder name | App URL | Source code repo (appfile) |
|---|---|---|
| collocations | [Kollokasjoner](https://beta.nb.no/dhlab/collocations/) |   |
| concordances | [Konkordanser](https://beta.nb.no/dhlab/concordances/) |  |
| corpus | [Konstruer et korpus](https://beta.nb.no/dhlab/corpus/) | Yoonsen/metadata ([corpus.py](https://github.com/Yoonsen/Metadata/blob/master/corpus.py)) |
| dispersion | [Narrative buer](https://beta.nb.no/dhlab/dispersion/) | Yoonsen/narrative-buer ([st_narrative.py](https://github.com/Yoonsen/narrative-buer/blob/master/st_narrative.py)) |
| document-term-matrix | [Ordfrekvenser](https://beta.nb.no/dhlab/ordfrekvenser/) | Yoonsen/Document-terms ([dtm_groupings.py](https://github.com/Yoonsen/Document_terms/blob/main/dtm_groupings.py)) |
| ner | [Navn og steder](https://beta.nb.no/dhlab/navn-og-steder/)  | Yoonsen/NER ([ner_app_urn.py](https://github.com/Yoonsen/NER/blob/master/ner_app_urn.py)) |
| ngram | [N-gram](https://beta.nb.no/dhlab/ngram-meta/) | Yoonsen/ngram_gui ([ngram_gui.py](https://github.com/Yoonsen/ngram_gui/blob/main/ngram_gui.py)) |
| subjects | [Emneord](https://beta.nb.no/dhlab/emneord/) |  Yoonsen/Word_to_topics ([emneord.py](https://github.com/Yoonsen/Word_to_topics/blob/main/emneord.py)) |
| themes | [Temaer](https://beta.nb.no/dhlab/temaer/) | Yoonsen/Document_thematic_analysis ([themes.py](https://github.com/Yoonsen/Document_thematic_analysis/blob/main/themes.py)) |


