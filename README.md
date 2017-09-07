GRC
===

[-link to website-](https://github.com/skwerlman/grc-temp-repo/)

Extract mod data:
```sh
cd src
./grc_conv.py ../GEMS-src/index.html ../out/modlist.yml
```


Current Roadmap
---------------

- **Tools for development**
	- Database
		- import mods
			- manually
			- nexus
			- steam
			- bethesda
		- export mod data
			- human readable
			- \[in format for web\]
		- assign tags to mods, based on tag list
			- nexus
			- steam
			- bethesda
	- Tags
		- add / delete / sort
			- extend list, if needed
		- edit
			- pair \[GRC\] tags with
				- nexus
				- steam
				- bethesda

- **Website** via GitHub
	- Front end
		- basic list display
		- basic filtering
	- Back end
		- \[Whatever backend needs\]

Current state
-------------

**DLC list**
DLCs extracted, waiting for tags
[dlc list](src/dlc.yml)

**Mod list**
Original GEMS mod list extracted, waiting for tags and verification
[modlist](out/modlist.yml)

**Tag list**
Tag list converted to xml format
[taglist](src/taglist.xml)

Cat:

![1cat](https://i.imgur.com/lVlPvCB.gif "A cat")
