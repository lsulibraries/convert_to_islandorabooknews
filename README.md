# ingest_to_islandora_helpers
Helper scripts for ingesting objects to islandora

These depend on:

  - ubuntu 14.04 (for jp2 support),
  - jdk 7 (for fits support -- you will have to sign up for an oracle account, as this version is no longer freely available),
  - python3,
  - python3-lxml,
  - imagemagick,
  - tesseract.

Virtualization is recommended.  Docker in particular, since collections may use an enormous amount of local disk space, which docker shares well.  A rough install process for this docker container is described in ingest_to_islandora_helpers/Book_Newspaper_Batch/stepsForMakingBookDerivDocker.txt.  Rough is the key word, as you'll have trouble finding jdk7, etc and configuring it to work.  A good dev would have made the docker build file comprehensive, but I am not that developer today.  Sorry.

  
