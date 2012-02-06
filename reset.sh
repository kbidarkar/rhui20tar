#!/bin/bash
#Reset the rhui20 folder for another installation or a failed install
rm  ./*.bkp answers_* network pulp1 pulp.conf rhua.conf host.sh run_distribute.sh
#rm -rf rhui20-iso rhui20-iso.tar
cp ./ans_dist_bkp/run_distribute.sh ./ans_dist_bkp/host.sh ./ans_dist_bkp/answers_file ./
