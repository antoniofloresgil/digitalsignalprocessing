# Convenience wrappers around the book container (Linux, macOS, WSL).
# Nothing besides Docker needs to be installed on the host.
IMAGE  ?= dsp-book:dev
DOCKER  = docker run --rm --platform linux/amd64 \
          --user "$$(id -u):$$(id -g)" --env HOME=/tmp \
          --mount "type=bind,source=$(CURDIR),target=/work"

.PHONY: image render html pdf preview lab shell clean

image:            ## Build the container image
	docker build --platform linux/amd64 -f docker/Dockerfile -t $(IMAGE) .

render: image     ## Render HTML and PDF into _book/
	$(DOCKER) --network none $(IMAGE) quarto render

html: image       ## Render only the HTML edition
	$(DOCKER) --network none $(IMAGE) quarto render --to live-html

pdf: image        ## Render only the PDF edition
	$(DOCKER) --network none $(IMAGE) quarto render --to pdf

preview: image    ## Live preview at http://localhost:4200
	$(DOCKER) -it --publish 127.0.0.1:4200:4200 $(IMAGE) \
	  quarto preview --host 0.0.0.0 --port 4200 --no-browser

lab: image        ## JupyterLab at http://localhost:8888 to play with the code
	$(DOCKER) -it --publish 127.0.0.1:8888:8888 $(IMAGE) \
	  jupyter lab --ip 0.0.0.0 --port 8888 --no-browser --ServerApp.token=''

shell: image      ## Interactive shell inside the container
	$(DOCKER) -it $(IMAGE) bash

clean:            ## Remove rendered output and execution caches
	rm -rf _book _freeze .quarto
