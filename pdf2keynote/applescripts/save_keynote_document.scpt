on run argv
    set filepath to item 1 of argv as POSIX file

    tell application "Keynote"
        tell the front document
            save in filepath
            close
        end tell
    end tell
end run
