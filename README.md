# aureo
numismatic database cartographer

-------------------

## Requirements
* `argparse`
* `folium`

## Install
```
pip install https://github.com/dantaki/aureo/releases/download/0.0.1/aureo-0.0.1.tar.gz
```
--------

## Usage
```
       d888 8888     888 8888888b.  8888888888 .d88888b.  
      d8888 8888     888 888   Y88b 888       d88P" "Y88b 
     d88P88 8888     888 888    888 888       888     888 
    d88P 88 8888     888 888   d88P 8888888   888     888 
   d88P  88 8888     888 8888888P"  888       888     888 
  d88P   88 8888     888 888 T88b   888       888     888 
 d888888888 8Y88b. .d88P 888  T88b  888       Y88b. .d88P 
d88P     88  "Y88888P"   888   T88b 8888888888 "Y88888P"  
             
             numismatic database cartographer 
---------------------------------------------------------
Version:  0.0.1
Author:   Danny Antaki <dantaki at ucsd dot com>
About:    map generator for coin collections
Usage:    aureo [-h] <-db database> <-loc locations> [options]

Required Arguments:
    -db     PATH      coin database file
    -loc    PATH      mint location file 

Options:
    -img    PATH      folder containing images
    -w      STR       weight unit [default: g] 
    -o      STR       output prefix [default: aureo]
    -h                print this message and exit

Notes:
    the database and location file must be tab delimited

    for an example of the database file, please refer to 
    coindb.txt on github: https://github.com/dantaki/aureo

    the location file must contain this header in this order:
    'Mint Latitude Longitude' with decimal coordinates

    images must be jpegs 800 x 800 pixels, 300 dpi
    filenames must be in this exact format: 
        ImagePrefix.[obv|rev].jpg

    the 'ImagePrefix' column in the database file must
    defined to include images in aureo maps

```
-------

## Imput Format

* `-loc` : Mint Location File
  * tab delimited
  * Required Columns:
    * Mint
    * Latitude 
    * Longitude
  * Decimal coordinates

* `-db` : Coin Data Base File
  * [example](https://github.com/dantaki/aureo/blob/master/coindb.txt)
  * tab delimited
  * Required Columns:
    * MinDate
    * MaxDate
    * Denomination
    * Authority
    * RIC
    * Mint
    * Region
    * Obverse
    * ObverseType
    * Reverse
    * ReverseType
    * Mintmark
    * Weight
    * Notes
  * Optional Columns:
    * ImagePrefix
    
-----

## Image Support

* `-img` takes the path to the images
* Image filename must match the `ImagePrefix` column in the `-db` file
* Image filename format:
  * `ImagePrefix.[obv|rev].jpg`

--------

## Author
[Danny Antaki](https://dantaki.github.io)
`dantaki at ucsd dot edu`
