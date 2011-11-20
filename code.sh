#!/bin/sh

function func {
	for i in *
	do
		if test -d $i ; then
            (cd $i
            func
            cd ..)
        else
            if echo "$i" | grep -E "*\.py$" >> /dev/null; then
				cat $i | sed 's/\t/    /g' > "$i.old"
				mv "$i.old" "$i"
            fi
        fi
	done
    
}

func ./
