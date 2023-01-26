# Custom Tkinter Widgets

This package contains a collection (*ok, only one so far*) of 
custom Tkinter tk and ttk widgets that I've created.  While I kept
generality in mind, these were all created to meet a specific 
need.  I am open to suggestions for exanding the capabilities
of any of these, but make no apology for any currently lacking
feature you may wish to have seen.

## PlaceholderEntry

This is a subclass of ttk.Entry.  It behaves identically to ttk.Entry
with the exception that if the entry is empty and the widget does not
have focus, it displays a placholder message.  By default, this 
placeholder is displayed in an italicised version of the Entry font
and in a dimmed color.  Optionally, the exact font, whether or not to
italicize the default font, and the placehold color may be specified
when instantiating the PlaceholderEntry widget.
