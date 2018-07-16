# For running within an Islandora vagrant box:

## From inside the dora box:

sudo apt install wget zip software-properties-common -y

sudo add-apt-repository ppa:deadsnakes/ppa

sudo apt update

sudo apt upgrade

sudo apt install python3-pip python3.6-dev cython3 pdftk build-essential libpoppler-cpp-dev pkg-config libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk python-dev libxml2 libxml2-dev libxslt-dev libxml2

rm /usr/bin/python3

ln -s /usr/bin/python3.6 /usr/bin/python3

sudo pip3 install pdftotext jpylyzer Pillow lxml



## Get the source institution-namespace-cpd.zip or institution-namespace-pdf.zip into the dora build.  (Scp, shared folder, or elsewise.)

sudo scp my_outside_username@130.39.63.207:/home/my_outside_username/Desktop/inst-namespace-pdf.zip /tmp/

## Unzip the file somewhere inside dora.

mkdir inst-namespace-pdf

sudo chown vagrant:vagrant inst-namespace-pdf.zip

mv inst-namespace-pdf-to-book.zip inst-namespace-pdf-to-book/

cd inst-namespace-pdf-to-book/

unzip inst-namespace-pdf-to-book.zip

mv inst-namespace-pdf-to-book.zip ..

## Convert a jp2 compound ingest package to a book/newspaper ingest package

cd /tmp

git clone https://github.com/lsulibraries/ingest_to_islandora_helpers

cd /tmp/ingest_to_islandora_helpers/Book_Newspaper_Batch/

python3 convert_jp2cpd_to_book_with_derivs.py input/file/path/institution-namespace-cpd

## or convert a pdf ingest package to a book/newspaper ingest package

cd /tmp

git clone https://github.com/lsulibraries/ingest_to_islandora_helpers

cd /tmp/ingest_to_islandora_helpers/Book_Newspaper_Batch/

python3 convert_pdf_to_book_with_derivs.py input/file/path/institution-namespace-pdf

If the process breaks, you can delete the most recent folders & the script will skip the ones you've already made.  However, if any folders are partially made, it will skip them too -- so when in doubt, delete the output folders.

## QA the output when done

sudo python3 validate_obj_mods.py {output_folder}

## Remove all file restrictions & zip the folder

sudo chmod -R u+rwX,go+rX,go-w {output_folder}

zip -r -0 {/tmp/whatever_filename.zip} {output_folder}

## Get the zip file out of dora onto your computer.  For example, from inside the dora, I used:

sudo scp /tmp/inst-namespace-pdf-to-book.zip my_outside_username@130.39.63.207:/home/my_outside_username/Desktop/ 



# It is possible to run these within a docker box, but that involves these hurdles:

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
