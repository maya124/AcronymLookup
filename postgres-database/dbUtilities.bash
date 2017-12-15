#!/bin/bash

if [ "$1" == 'dump' ]
then
    pg_dump -U 'acronym_user' --host=localhost --data-only --inserts 'acronyms' > acronyms.pgsql
elif [ "$1" == 'load' ]
then
    psql -U 'acronym_user' --host=localhost acronyms < acronyms.pgsql
elif [ "$1" == 'updateSchema' ]
then
    read -p "Are you sure you want to drop all tables? " -n 1 -r
    echo    # (optional) move to a new line
    if [[ $REPLY =~ ^[Yy]$ ]]
    then
        echo "Now dropping tables..."
        dropdb -U 'acronym_user' --host=localhost acronyms
        echo "Now creating new database 'acronyms'"
        createdb -U 'acronym_user' --host=localhost acronyms
        echo "Now loading schema from file..."
        psql -U 'acronym_user' --host=localhost acronyms < setUpDb.sql
    fi
else
    echo "Invalid command. Options are: 'dump', 'load' and 'updateSchema'"
fi

        
   
