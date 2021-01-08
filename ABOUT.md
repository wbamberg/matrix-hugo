
This document describes the components of the new spec platform, and the changes that have been made to the old spec content to make it work in the new platform.

It lists each top-level directory in the repo and describes what it contains and what it does in the platform.

## assets

This contains:
* the Matrix logo, which we're including in the header.
* Sass files we're using to customise the styles provided by our Hugo theme (Docsy).

## changelog

This contains towncrier-formatted metadata and newsfragments. There's more information about this directory in the issue about specification versions: https://github.com/matrix-org/matrix-doc/issues/2877.

## content

This is where the specification's prose content lives. In Hugo "/content" is the default directory for page content, and by default MD files in here get published as web pages, with the URL structure mirroring the directory structure.

The content here is taken from the "/specification" directory in matrix-doc.
The main changes from the old spec content are:

* all prose is MD, not RST

* batesian template calls are replaced with Hugo template calls

* appendices are maintained in a single file, rather than each appendix getting its own file

* there's a new changelog.md, as the changelog is now its own page

As in the old spec (and following the discussion in https://github.com/matrix-org/matrix-doc/issues/2838), we maintain modules in separate files, under "client-server/modules". But I've included "feature_profiles" in the main client-server spec. Also, I've pushed the heading levels for module files down so they match their destination, rather than having to adjust heading levels in the build process.

## data

This is where we keep specification data - OpenAPI data, event schemas and examples, and the "server-signatures.yaml" file.

By default, Hugo will let templates access YAML, JSON, or TOML files under "/data" directly as dictionaries, without the templates needing to load them as files: https://gohugo.io/templates/data-templates/. We take advantage of that feature here.

This data is taken from the following places in matrix-doc:

* "/api": OpenAPI specifications
* "/event-schemas": event schemas and examples
* "/schemas": the "server-signatures.yaml" file

I've made a few changes to this data:

* Many files under "/event-schemas" don't have an extension. Hugo complains if files under "/data" don't have an extension. So I've given (YAML) extensions to the data files that didn't have one.

* Because of this, I've had to change "$ref" schema values to include the extension.

* In the old spec, "/api/client-server/definitions" has a symlink to "/event-schemas". This doesn't work with accessing-data-as-objects, so I've removed the symlink and used relative paths in "$ref" values instead.

* In all data files, "description" fields contained RST. I've updated this to MD. Mostly this is a matter of updating links and `code` formatting, and rewriting `... Note` and `... Warning` directives. There are a couple of tables I had to rewrite.

Note also that I've just removed everything that wasn't a data file - this includes for example all the code in "/api/files" that I guess is used to build the API playground? If we still want to support this we will need to find a home for it.

## data-definitions

This contains only the sas-emoji stuff. I would have put this into "/data" as well, except we are not allowed to move it.

## layouts

This contains Hugo templates.

There are three directories under "/layouts":

* docs
* partials
* shortcodes

### layouts/docs

These templates control the overall layout of our pages.

### layouts/partials

Partials are templates that can be called by other templates. The canonical use of them is to make reusable bits of content, like breadcrumbs and sidebars. But they can also be called by shortcodes, and can return values, so we are also using them to factor out common operations into separate modules.

* `alert`: common code for note, rationale, and warning boxes
* `breadcrumbs`, `navbar`, `sidebar-tree`, `version-banner`: partials for various page elements, taken from Docsy but modified for our purposes.
* `hooks/body-end`: this is included in all pages at the end of `<body>`. We use it to include custom JS, which is used to fix up heading IDs and generate the ToC.
* `hooks/head-end`: this is included in all pages at the end of `<head>`. We use it to include the modifications and extensions we've made to the default CSS that is included in Docsy.

Most significantly, partials do most of the work to render content from OpenAPI/Swagger data and event schemas.

* `events/render-event`: renders an event from an event schema object.
* `openapi/*`: various templates to render an HTTP API from OpenAPI data. These call each other as follows:

```
render-api
    -> render-operation
        -> render-request        -> render-object-table
            -> render-parameters -> render-object-table
        -> render-responses      -> render-object-table
```

* `json-schema`: this provides basic support for working with JSON schema and is called by both `render-event` and the `openapi` templates. It includes templates to handle the `$ref` and `allOf` keywords. This is probably the most complicated bit of code here and could definitely use some careful review.

### layouts/shortcodes

Shortcodes are templates that can be called directly from content. All the existing Batesian templates should have an analogous shortcode.

* `boxes/note`, `boxes/rationale`, `boxes/warning`: replace Note, Rationale, Warning RST directives.
* `changelog/changelog-changes`, `changelog/description`: used to build changelogs, including generating content from newsfragments.
* `cs-modules`: called from the client-server spec to embed all the modules.
* `definition`: replaces the old {{definition_*}} template.
* `event-fields`: replaces the old {{common_event_fields}} and {{common_room_event_fields}} templates.
* `event-group`: replaces the old {{*_events}} template.
* `event`: replaces the old {{*_event}} template.
* `http-api`: replaces the old {{*_http_api}} template.
* `msgtypes`: replaces the old {{msgtype_events}} template.
* `sas-emojis`: replaces the old {{sas_emoji_table}} template.

## static

This includes static assets that don't need processing (assets that do need processing, such as SCSS, live in /assets):

* /icons
* /js/toc.js -> client-side JS to implement the table of contents

## themes

This contains the Docsy theme as a submodule, which in turn pulls in Bootstrap and Font Awesome as submodules. Since we're not using much of these, it might make sense at some point to carve out the bits we are using and discard the rest.

## significant top-level files

### config.toml

Hugo config file. This starts with the Docsy config and makes a few changes. Notable things we have added:=

* `params.version.status`: indicates the status of this version, one of "unstable", "current", "historical".
* `params.version.current_version_url`: points to the URL for the  current version.
* `params.version.major_version`, `params.version.minor_version`, `params.version.patch_version`: used to describe the actual version number for this version. These are omitted if the current version status is "unstable".

### package.json

We unfortunately apparently have to have a Node dependency, I think for autoprefixing CSS properties.
