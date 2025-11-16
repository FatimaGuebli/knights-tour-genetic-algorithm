Place any .ttf or .otf font files you want the application to use into the `fonts` folder.

The menu code will look for the first .ttf/.otf file and load it for the title and buttons. If no font files are found it will fall back to the system font.

Example:
 - interface/fontsassets/fonts/OpenSans-Regular.ttf
 - interface/fontsassets/fonts/YourFont.otf

After adding fonts, re-run `python main.py` to see them used by the menu.
