on run argv
    set lastIndex to item 1 of argv as number
    set soundFile to item 2 of argv as POSIX file
    set x to item 3 of argv as number
    set y to item 4 of argv as number
    set theFilePath to soundFile as alias

    tell application "Keynote"
        tell the front document
            -- get document dimensions
            set docWidth to the width
            set docHeight to the height
            
            tell slide lastIndex
                -- Keynote does not support using the audio clip class with the make verb
                -- Import the audio file by using the image class as the direct parameter
                -- The returned object reference will be to the created audio file
                set thisMovie to make new image with properties {file:theFilePath}
                tell thisMovie
                    -- adjust the size and position of the movie item...
                    -- using properties inherited from iWork Item class
                    set movWidth to 720
                    set width to movWidth
                    set movHeight to height
                    set position to ¬
                        {(docWidth - movWidth) div 2, (docHeight - movHeight) div 2}
                    set repetition method to none
                end tell
            end tell
        end tell
    end tell
end run
