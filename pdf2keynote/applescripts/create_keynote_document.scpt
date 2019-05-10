on run argv
    set w to item 1 of argv as integer
    set h to item 2 of argv as integer
    tell application "Keynote"
        activate
        set thisDocument to ¬
            make new document with properties ¬
                {document theme:theme "White", width:w, height:h}
    end tell
end run
