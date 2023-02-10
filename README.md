# Custom Tkinter Widgets

This package contains a collection (*ok, only two so far*) of 
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

## StatusLabel

This is a subclass of tk.Label.  What makes it different is the
notion of "status state".  The widget can be in one of four 
distinct states: normal, info, warning, or error.  The widget
provides variants on each of the standard tk.Label appearance
options so that it can be configured to appear differently for
each of these states.  The widget provides four methods which 
can be used to modify the state and the text being shown.
