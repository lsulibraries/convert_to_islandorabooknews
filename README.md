# Overview

You can use the docker-compose box or the lsulibraries/dora box.  The docker version has these benefits:

- can use all your computer's CPU/RAM/disk space 
- allows other programs to use the CPU/RAM/disk

The dora build is also a valid option, but it requires some additional setup (described below).  It is more heavyweight on your computer.

## Using the docker-compose box:

The workflow is this:

- install docker and docker-compose, as described in the lsulibraries/gnatty github repo readme.
- copy jdk-7u80-linux-x64.tar.gz from the R drive, save it into the ./required_libraries/ folder
- copy fits-0.8.5.zip from the R drive, save it into the ./required_libraries/ folder
- copy your \*\-cpd.zip or \*\-pdf.zip file from the U drive, save it into the ./source_data/ folder.

- this repo folder is shared inside the box as /ingest_to_islandora_helpers.  There's no need to enter the box.

- build the docker box with `docker-compose up --build -d`
- convert a jp2cpd collection to a book/newspaper ingest format using:
	- `docker-compose exec book_newspaper_box python3 convert_jp2cpd_to_book_with_derivs.py /ingest_to_islandora_helpers/source_data/{namespace-collection}-cpd.zip`
- convert a pdf collection to a book/newspaper ingest format using:
	- `docker-compose exec book_newspaper_box python3 convert_pdf_to_book_with_derivs.py /ingest_to_islandora_helpers/source_data/{namespace-collection}-pdf.zip`

- to see the logs:
	- `docker-compose logs book_newspaper_box`

- If the process breaks, you can delete the most recent folders & the script will skip the ones you've already made.  However, if any folders are partially made, it will skip them too -- so when in doubt, delete the output folders.

- when finished, the output files will be at ingest_to_islandora_helpers/source_data/{namespace-collection-origformat}-to-book/

- you may wish to validate them, using `docker-compose exec python3 validate_obj_mods.py /ingest_to_islandora_helpers/source_data/{namespace-collection-origname}-to-book/`


## Using a dora vagrant box:

- Add dependencies

```sudo apt install wget zip software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt upgrade
sudo apt install python3-pip python3.6-dev cython3 pdftk build-essential libpoppler-cpp-dev pkg-config libtiff4-dev libjpeg8-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev tcl8.5-dev tk8.5-dev python-tk python-dev libxml2 libxml2-dev libxslt-dev libxml2
rm /usr/bin/python3
ln -s /usr/bin/python3.6 /usr/bin/python3
sudo pip3 install pdftotext jpylyzer Pillow lxml
```

- Get the source institution-namespace-cpd.zip or institution-namespace-pdf.zip into the dora build.  (Scp, shared folder, or elsewise.)

`sudo scp my_outside_username@130.39.63.207:/home/my_outside_username/Desktop/inst-namespace-pdf.zip /tmp/`

- Unzip the file somewhere inside dora.

```mkdir inst-namespace-pdf
sudo chown vagrant:vagrant inst-namespace-pdf.zip
mv inst-namespace-pdf.zip inst-namespace-pdf/
cd inst-namespace-pdf/
unzip inst-namespace-pdf.zip
mv inst-namespace-pdf.zip ..
```

- Convert a jp2cpd ingest package to a book/newspaper ingest package

```
cd /tmp
git clone https://github.com/lsulibraries/ingest_to_islandora_helpers
cd /tmp/ingest_to_islandora_helpers/Book_Newspaper_Batch/
python3 convert_jp2cpd_to_book_with_derivs.py input/file/path/institution-namespace-cpd
```

- or convert a pdf ingest package to a book/newspaper ingest package

```
cd /tmp
git clone https://github.com/lsulibraries/ingest_to_islandora_helpers
cd /tmp/ingest_to_islandora_helpers/Book_Newspaper_Batch/
python3 convert_pdf_to_book_with_derivs.py input/file/path/institution-namespace-pdf/
```

- QA the output when done

`sudo python3 validate_obj_mods.py {output_folder}`

- Remove all file restrictions & zip the folder

```
sudo chmod -R u+rwX,go+rX,go-w {output_folder}
zip -r -0 {/tmp/whatever_filename.zip} {output_folder}
```

- Get the zip file out of dora onto your computer.  For example, from inside the dora, I used:

`sudo scp /tmp/inst-namespace-pdf-to-book.zip my_outside_username@130.39.63.207:/home/my_outside_username/Desktop/ `
