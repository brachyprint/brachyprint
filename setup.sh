#!/bin/sh

# script to download redfred data and decompress it

rf_file="redfred.tar.bz2"

rf_url="http://www.equipmentverification.co.uk/redfred/$rf_file"

output_dir="data"

mkdir -p $output_dir
cd $output_dir

# download redfred if required
if [ ! -f "$rf_file" ]; then
    wget $rf_url
fi

echo "Decompressing redfred..."

tar -xjf $rf_file

