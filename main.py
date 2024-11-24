# main.py

import argparse
import sys
import time
from GrapplerModules.data_processing import process_data, generic_function
from GrapplerModules.log_processing import run_grep_once
import subprocess


def main():

    parser = argparse.ArgumentParser(description='Process data.')
    parser.add_argument("-jo", "--json_output", help="Write output to a json file.", action="store_true")
    parser.add_argument("-f", "--add_file", help="Add new queries json file.")
    parser.add_argument("-p", "--permiso_intel", help="Output permiso intel.", action="store_true")
    parser.add_argument("-q", "--query", help="Add query/ies", required=False)
    parser.add_argument("-s", "--source_type", help="Add source type to query for", default="*",  required=False)
    parser.add_argument("-sd", "--start_date", help="Optionally filter on Objects modified after a Date or Time. E.g. 2022-01-01",required=False)
    parser.add_argument("-ed", "--end_date", help="Optionally filter on Objects modified before a Date or Time. E.g. 2022-01-01 ", required=False)
    parser.add_argument("-fs", "--file_size", help="Optionally filter on Objects smaller than a file size, in bytes. Defaults to 100 Mb. ", default=100000000,)
    
    
    args = parser.parse_args()
    banner ="""
                                                                               .____
                                                                        ____.((`    ))`.__
                                                                    ..((`                `))__
                                                                ,__.((`      _       _        `)) 
                                                               ((`          | \     / |         ))__
                                                            ,_.((           (\033[91m\033[1m @ \033[00m\ / \033[91m\033[1m@ \033[00m)            `))
                                                           ((                '-_-"..^..               ))
                                                          ((` \033[33m\033[1m  __     _  \033[00m      _^^   ^^_              ))'  
                                                          ((  \033[33m\033[1m /  \  // \   \033[00m                           ))'  
                                                           (( `\033[33m\033[1m    \//___.   \033[00m                        ))
                                                           '.____ \033[33m\033[1m //\033[00m_____\033[33m\033[1m\ \033[00m_______________________.' 
 \033[33m\033[1m                                                  \033[33m\033[1m               //\033[00m \033[33m\033[1m     / \033[00m
                                                                 \033[33m\033[1m// \033[00m      `
 \033[33m\033[1m                                                   .===.       //\033[00m
 \033[33m\033[1m                                ,+~+,           .XP    qP    .P"\033[00m
  \033[33m\033[1m                            /7PP=~=PP,_____,pP^       xp..PP"\033[00m
\033[93m\033[1m  |-----------------. \033[33m\033[1m     ..//       ^PERMISO^           '^^
\033[93m\033[1m  ( \033[94m\033[1m PERMISO P0 LABS\033[00m\033[38;5;208m\033[1m `>=====/\033[0m
\033[93m\033[1m  |\033[94m\033[1m  INTEL\033[00m\033[93m\033[1m, ________/
\033[93m\033[1m  \   (_6_)
\033[93m\033[1m  |    |
\033[93m\033[1m  /____|\033[00m 

'@
.------..------..------..------..------..------..------..------..------..------..------..------..------.
|\033[00m\033[91m\033[1mC.--. \033[0m||\033[00m\033[91m\033[1mL.--. \033[0m||\033[00m\033[91m\033[1mO.--. \033[0m||\033[00m\033[91m\033[1mU.--. \033[0m||\033[00m\033[91m\033[1mD.--. \033[0m||\033[00m\033[91m\033[1mG.--. \033[0m||\033[00m\033[91m\033[1mR.--. \033[0m||\033[00m\033[91m\033[1mA.--. \033[0m||\033[00m\033[91m\033[1mP.--. \033[0m||\033[00m\033[91m\033[1mP.--. \033[0m||\033[00m\033[91m\033[1mL.--. \033[0m||\033[00m\033[91m\033[1mE.--. \033[0m||\033[00m\033[91m\033[1mR.--. \033[0m|
|\033[00m\033[91m\033[1m :/\: \033[0m||\033[00m\033[91m\033[1m :/\: \033[0m||\033[00m\033[91m\033[1m :/\: \033[0m||\033[00m\033[91m\033[1m (\/) \033[0m||\033[00m\033[91m\033[1m :/\: \033[0m||\033[00m\033[91m\033[1m :/\: \033[0m||\033[00m\033[91m\033[1m :(): \033[0m||\033[00m\033[91m\033[1m (\/) \033[0m||\033[00m\033[91m\033[1m :/\: \033[0m||\033[00m\033[91m\033[1m :/\: \033[0m||\033[00m\033[91m\033[1m :/\: \033[0m||\033[00m\033[91m\033[1m (\/) \033[0m||\033[00m\033[91m\033[1m :(): \033[0m|
|\033[00m\033[91m\033[1m :\/: \033[0m||\033[00m\033[91m\033[1m (__) \033[0m||\033[00m\033[91m\033[1m :\/: \033[0m||\033[00m\033[91m\033[1m :\/: \033[0m||\033[00m\033[91m\033[1m (__) \033[0m||\033[00m\033[91m\033[1m :\/: \033[0m||\033[00m\033[91m\033[1m ()() \033[0m||\033[00m\033[91m\033[1m :\/: \033[0m||\033[00m\033[91m\033[1m (__) \033[0m||\033[00m\033[91m\033[1m (__) \033[0m||\033[00m\033[91m\033[1m (__) \033[0m||\033[00m\033[91m\033[1m :\/: \033[0m||\033[00m\033[91m\033[1m ()() \033[0m|
|\033[00m\033[91m\033[1m '--'C\033[0m||\033[00m\033[91m\033[1m '--'L\033[0m||\033[00m\033[91m\033[1m '--'O\033[0m||\033[00m\033[91m\033[1m '--'U\033[0m||\033[00m\033[91m\033[1m '--'D\033[0m||\033[00m\033[91m\033[1m '--'G\033[0m||\033[00m\033[91m\033[1m '--'R\033[0m||\033[00m\033[91m\033[1m '--'A\033[0m||\033[00m\033[91m\033[1m '--'P\033[0m||\033[00m\033[91m\033[1m '--'P\033[0m||\033[00m\033[91m\033[1m '--'L\033[0m||\033[00m\033[91m\033[1m '--'E\033[0m||\033[00m\033[91m\033[1m '--'R\033[0m|
`------'`------'`------'`------'`------'`------'`------'`------'`------'`------'`------'`------'`------'
                                                                         
        """
    for char in banner:
        sys.stdout.write(f"{char}")
        sys.stdout.flush()
        time.sleep(0.0001)

    if args.query:
        run_grep_once()
        process_data(args.permiso_intel, args.add_file, args.query, args.source_type, args.json_output, args.start_date, args.end_date, args.file_size)
        
    else:
        run_grep_once()
        combined_data, source_types, intel = process_data(args.permiso_intel, args.add_file, args.query, args.source_type, args.json_output, args.start_date, args.end_date, args.file_size)
        generic_function(combined_data, source_types, args.json_output, args.start_date, args.end_date, args.file_size, intel)
if __name__ == "__main__":
    main()
