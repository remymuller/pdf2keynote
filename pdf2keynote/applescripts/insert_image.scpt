on run argv
    set lastIndex to item 1 of argv as number
    set theImage  to item 2 of argv as POSIX file

    tell application "Keynote"
        tell the front document
            set docWidth to its width
            set docHeight to its height
            tell slide lastIndex
                make new image with properties { file: theImage, width: docWidth, height: docHeight, position: {0,0} }
            end tell
        end tell
    end tell
end run
