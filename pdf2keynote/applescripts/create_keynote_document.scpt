tell application "Keynote"
	activate
	set thisDocument to ¬
		make new document with properties ¬
			{document theme:theme "White", width:1024, height:768}
end tell
