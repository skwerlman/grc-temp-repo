GEMS Recreation Committee - GRC
===============================

[-link to website-](https://github.com/skwerlman/grc-temp-repo/)

Extract mod data:
```sh
cd src
./grc_conv.py ../GEMS-src/index.html ../out/modlist.yml
```


Current Roadmap
---------------

- [ ] **Tools for development**
	- [ ] Database [modlist](out/modlist.yml) [dlc list](src/dlc.yml)
		- [x] extraxt DLCs and original modlist
		- [ ] import mods
			- [ ] manually
			- [ ] nexus
			- [ ] steam
			- [ ] bethesda
		- [ ] export mod data
			- [ ] human readable
			- [ ] \[in format for web\]
		- [ ] assign tags to mods, based on tag list
			- [ ] nexus
			- [ ] steam
			- [ ] bethesda
	- [ ] Tags [taglist](src/taglist.xml)
		- [ ] add / delete / sort
			- [ ] extend list, if needed
		- [ ] edit
			- [ ] pair \[GRC\] tags with
				- [ ] nexus
				- [ ] steam
				- [ ] bethesda
- [ ] **Website** via GitHub
	- [ ] Front end
		- [ ] basic list display
		- [ ] basic filtering
	- [ ] Back end
		- [ ] GitHub pages up
		- [ ] Generated page
- [ ] **Misc**
	- [ ] Set up a proper GH org
		- [ ] Decide on a name


Cat:

![1cat](https://i.imgur.com/lVlPvCB.gif "A cat")
