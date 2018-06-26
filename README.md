# ingest_to_islandora_helpers
Helper scripts for ingesting objects to islandora

These depend on:

  - ubuntu 14.04 (for jp2 support),
  - jdk 7 (for fits support -- you will have to sign up for an oracle account, as this version is no longer freely available),
  - python3,
  - python3-lxml,
  - imagemagick,
  - tesseract,
  - fits 0.8.5,
  - kdu_compress 7 (kakadu)

Virtualization is recommended.  You can start up a dora vagrant box (the Islandora dev box) and install python3.6, pip install things, git clone the repo, & run a Book conversion inside there.  That has the advantage of already having the correct version of fits, java, kakadu, etc.  The disadvantage is if the collection is larger than the dora box.

Docker has some advantages, since it shares harddrive space & CPUs with the host computer, and converting collections may use an enormous amount of both.  The disadvantage is the difficulty setting up the docker container.  A rough install process for this docker container is described in ingest_to_islandora_helpers/Book_Newspaper_Batch/stepsForMakingBookDerivDocker.txt.  Rough is the key word, as you'll have trouble finding jdk7, fits0.8.5, kakadu7, etc and configuring it to work.  A good dev would have made the docker build file comprehensive, but I'm not there yet.
