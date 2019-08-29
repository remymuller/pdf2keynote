on run argv
    set lastIndex to item 1 of argv as number
    set soundFile to item 2 of argv as POSIX file
    set x to item 3 of argv as number
    set y to item 4 of argv as number
    set theFilePath to soundFile as alias

    tell application "Keynote"
        tell the front document
            tell slide lastIndex
                -- Keynote does not support using the audio clip class with the make verb
                -- Import the audio file by using the image class as the direct parameter
                -- The returned object reference will be to the created audio file
                set thisAudioClip to make new image with properties {file:theFilePath}
                tell thisAudioClip
                    -- position property inherited from iWork Item class
                    set position to {x, y}
                    -- audio clip properties
                    -- set clip volume to 75
                    -- set repetition method to loop
                    -- place the locked property at the end because
                    -- you can't change the properties of a locked iWork item
                    --set locked to true
                end tell
            end tell
        end tell
    end tell
end run
