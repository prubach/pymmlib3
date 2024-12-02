#!/bin/bash
# Create Monomer library, taking as input the path to the downloaded components.cif file and some temporary directory to use when processing. This script can also generate a Monomers.zip if the third option is set to YES
CIF_FILE=$1
WORKING_DIR=$2
OUTPUT_FILE=$3
IS_ZIP=$4
if [ -d "$WORKING_DIR" ]; then rm -Rf $WORKING_DIR; fi
mkdir $WORKING_DIR
cd $WORKING_DIR
csplit ${CIF_FILE} /data_/ '{*}' --prefix=monom > /dev/null 
rm -f monom00
for mmf in `ls monom*`; do
  mm=`cat ${mmf} | grep data_ | cut -d "_" -f 2`
  if [ "$IS_ZIP" = "YES" ]; then
    mv ${mmf} ${mm}
  else
    submm=`echo ${mm} | cut -b 1`
    if [ ! -d "${submm}" ]; then mkdir $submm; fi
    mv ${mmf} ${submm}/${mm}
  fi
done
if [ "$IS_ZIP" = "YES" ]; then
  zip ${OUTPUT_FILE} * > /dev/null
fi
