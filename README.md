# This repo has been archived: Each DHLAB app now has its own repo with the following prefix dhlab-app-*

# Web applications from NB DHLAB

This repo contains source code for various web applications provided by the DHLAB of the National Library of Norway. The web applications are hosted here: https://www.nb.no/dh-lab/apper

## Example usage

```bash
cd collocations
docker build -t nb-collocations .
docker run --rm -p 5001:5001 nb-collocations
```

