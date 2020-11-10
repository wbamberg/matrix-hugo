# Matrix specification in Hugo

This repository contains a version of the Matrix specification running in a [Hugo](https://gohugo.io/) instance, using the [Docsy](https://github.com/google/docsy) theme.

It is currently built and published using Netlify: if you just want to see what the rendered pages are like, visit https://adoring-einstein-5ea514.netlify.app/.

## For spec editors

### Getting started

Install Hugo, following the instructions at https://gohugo.io/getting-started/installing/ .

Clone this repo and its submodules, with a command like:

    git clone --recurse-submodules --depth 1 https://github.com/wbamberg/matrix-hugo

Now from the root "matrix-hugo" directory, run:

    hugo server  --disableFastRender

This command should build the site and start the server. It should also tell you where to point your browser, with a line like:

    Web Server is available at //localhost:1313/ (bind address 127.0.0.1)

While the server is running Hugo will watch for changes to the spec content and rebuild the site. You can omit `--disableFastRender`, but including it makes it more likely that Hugo will pick up changes to the spec content.

### Editing the spec

The spec content is kept in two places:

* prose is stored as Markdown files inside the `/content/en/` directory
* data, including the OpenAPI and event schemas, is stored as YAML files inside the `/data/` directory.
