# Readme Footer Generator

Generate links to the next and previous README files in the project

## Using the generator

From the root of the project, run:

```bash
docker run --rm -e DEBUG=True --volume $(PWD):/data ghcr.io/managedkaos/readme-footer-generator:main
```

> [!NOTE]
> The `-e DEBUG=True` flag is optional.  Use it to get insight into how the files are processed.
